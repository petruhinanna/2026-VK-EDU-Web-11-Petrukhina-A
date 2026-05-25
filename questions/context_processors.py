from django.contrib.auth.models import User
from django.db.models import Count, Q

from questions.models import Tag


def sidebar_data(request):
    if request.path.startswith('/admin/') or request.path.startswith('/__debug__/'):
        return {}

    popular_tags = (
        Tag.objects
        .annotate(
            question_count=Count(
                'questions',
                filter=Q(questions__is_active=True),
                distinct=True,
            )
        )
        .filter(question_count__gt=0)
        .order_by('-question_count', 'name')[:8]
    )

    top_users = (
        User.objects
        .annotate(
            question_count=Count(
                'questions',
                filter=Q(questions__is_active=True),
                distinct=True,
            )
        )
        .filter(question_count__gt=0)
        .order_by('-question_count', 'username')[:5]
    )

    return {
        'popular_tags': popular_tags,
        'top_users': top_users,
    }