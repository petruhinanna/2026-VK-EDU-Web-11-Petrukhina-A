from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models import Count, F, Q, Sum
from django.utils import timezone

from questions.models import Answer, Tag


POPULAR_TAGS_CACHE_KEY = 'sidebar:popular_tags'
BEST_USERS_CACHE_KEY = 'sidebar:best_users'

POPULAR_TAGS_CACHE_TIMEOUT = 60 * 60
BEST_USERS_CACHE_TIMEOUT = 60 * 60


def safe_cache_get(key):
    try:
        return cache.get(key)
    except Exception:
        return None


def safe_cache_set(key, value, timeout):
    try:
        cache.set(key, value, timeout)
    except Exception:
        pass


def get_popular_tags_from_db():
    three_months_ago = timezone.now() - timedelta(days=90)

    return list(
        Tag.objects
        .annotate(
            question_count=Count(
                'questions',
                filter=Q(
                    questions__is_active=True,
                    questions__created_at__gte=three_months_ago,
                ),
                distinct=True,
            )
        )
        .filter(question_count__gt=0)
        .order_by('-question_count', 'name')
        .values('name', 'slug', 'question_count')[:10]
    )


def get_best_users_from_db():
    week_ago = timezone.now() - timedelta(days=7)

    users = (
        User.objects
        .annotate(
            questions_rating=Sum(
                'questions__rating',
                filter=Q(
                    questions__is_active=True,
                    questions__created_at__gte=week_ago,
                ),
                default=0,
            ),
            answers_rating=Sum(
                'answers__rating',
                filter=Q(
                    answers__is_active=True,
                    answers__created_at__gte=week_ago,
                ),
                default=0,
            ),
        )
        .annotate(total_rating=F('questions_rating') + F('answers_rating'))
        .filter(total_rating__gt=0)
        .order_by('-total_rating', 'username')
        .values('username', 'id', 'total_rating')[:10]
    )

    return list(users)


@shared_task
def update_popular_tags_cache():
    popular_tags = get_popular_tags_from_db()

    safe_cache_set(
        POPULAR_TAGS_CACHE_KEY,
        popular_tags,
        POPULAR_TAGS_CACHE_TIMEOUT,
    )

    return len(popular_tags)


@shared_task
def update_best_users_cache():
    best_users = get_best_users_from_db()

    safe_cache_set(
        BEST_USERS_CACHE_KEY,
        best_users,
        BEST_USERS_CACHE_TIMEOUT,
    )

    return len(best_users)


def get_popular_tags():
    popular_tags = safe_cache_get(POPULAR_TAGS_CACHE_KEY)

    if popular_tags is None:
        popular_tags = get_popular_tags_from_db()

        safe_cache_set(
            POPULAR_TAGS_CACHE_KEY,
            popular_tags,
            POPULAR_TAGS_CACHE_TIMEOUT,
        )

    return popular_tags


def get_best_users():
    best_users = safe_cache_get(BEST_USERS_CACHE_KEY)

    if best_users is None:
        best_users = get_best_users_from_db()

        safe_cache_set(
            BEST_USERS_CACHE_KEY,
            best_users,
            BEST_USERS_CACHE_TIMEOUT,
        )

    return best_users


@shared_task
def send_new_answer_email(answer_id):
    try:
        answer = (
            Answer.objects
            .select_related('question', 'question__author', 'author')
            .get(id=answer_id)
        )
    except Answer.DoesNotExist:
        return 'answer_not_found'

    question = answer.question
    question_author = question.author

    if question_author is None:
        return 'question_has_no_author'

    if not question_author.email:
        return 'question_author_has_no_email'

    if answer.author_id == question_author.id:
        return 'author_answered_own_question'

    question_url = f'{settings.SITE_URL}{question.get_absolute_url()}#answer-{answer.id}'

    subject = 'Новый ответ на ваш вопрос'
    message = (
        f'Здравствуйте!\n\n'
        f'На ваш вопрос "{question.title}" появился новый ответ.\n\n'
        f'Посмотреть ответ можно здесь:\n'
        f'{question_url}\n'
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[question_author.email],
        fail_silently=False,
    )

    return 'sent'