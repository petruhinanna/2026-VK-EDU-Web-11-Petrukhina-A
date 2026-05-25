from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from questions.forms import (
    AnswerForm,
    AnswerLikeForm,
    CorrectAnswerForm,
    QuestionForm,
    QuestionLikeForm,
)
from questions.models import Answer, AnswerLike, Question, QuestionLike, Tag
from questions.utils import paginate


def add_question_votes(questions, user):
    if not user.is_authenticated:
        return

    question_ids = [question.id for question in questions]

    user_votes = dict(
        QuestionLike.objects
        .filter(user=user, question_id__in=question_ids)
        .values_list('question_id', 'value')
    )

    for question in questions:
        question.user_vote = user_votes.get(question.id)


def add_answer_votes(answers, user):
    if not user.is_authenticated:
        return

    answer_ids = [answer.id for answer in answers]

    user_votes = dict(
        AnswerLike.objects
        .filter(user=user, answer_id__in=answer_ids)
        .values_list('answer_id', 'value')
    )

    for answer in answers:
        answer.user_vote = user_votes.get(answer.id)


@ensure_csrf_cookie
def index(request):
    questions = Question.objects.new()
    page = paginate(questions, request, per_page=5)
    questions_on_page = list(page.object_list)

    add_question_votes(questions_on_page, request.user)

    return render(
        request,
        'questions/index.html',
        {
            'questions': questions_on_page,
            'page_obj': page,
        }
    )


@ensure_csrf_cookie
def hot(request):
    questions = Question.objects.best()
    page = paginate(questions, request, per_page=5)
    questions_on_page = list(page.object_list)

    add_question_votes(questions_on_page, request.user)

    return render(
        request,
        'questions/hot.html',
        {
            'questions': questions_on_page,
            'page_obj': page,
        }
    )


@ensure_csrf_cookie
def tag(request, tag_name):
    tag_obj = get_object_or_404(Tag, slug=tag_name)
    questions = Question.objects.by_tag(tag_name)
    page = paginate(questions, request, per_page=5)
    questions_on_page = list(page.object_list)

    add_question_votes(questions_on_page, request.user)

    return render(
        request,
        'questions/tag.html',
        {
            'questions': questions_on_page,
            'page_obj': page,
            'tag': tag_obj,
        }
    )


@ensure_csrf_cookie
def question_detail(request, question_id):
    question = get_object_or_404(
        Question.objects.with_related(),
        id=question_id,
    )

    answers = (
        question.answers
        .active()
        .select_related('author')
        .order_by('-created_at', '-id')
    )

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f'/login/?next={request.path}')

        form = AnswerForm(
            request.POST,
            author=request.user,
            question=question,
        )

        if form.is_valid():
            answer = form.save()
            return redirect(
                f'{question.get_absolute_url()}?page=1#answer-{answer.id}'
            )
    else:
        form = AnswerForm()

    page = paginate(answers, request, per_page=5)
    answers_on_page = list(page.object_list)

    add_question_votes([question], request.user)
    add_answer_votes(answers_on_page, request.user)

    return render(
        request,
        'questions/question.html',
        {
            'question': question,
            'answers': answers_on_page,
            'page_obj': page,
            'form': form,
        }
    )


@login_required(login_url='/login/')
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(
            request.POST,
            author=request.user,
        )

        if form.is_valid():
            question = form.save()
            return redirect(question.get_absolute_url())
    else:
        form = QuestionForm()

    return render(
        request,
        'questions/ask.html',
        {
            'form': form,
        }
    )


@require_POST
def question_like(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                'ok': False,
                'error': 'auth_required',
                'message': 'Войдите, чтобы оценивать вопросы.',
            },
            status=401,
        )

    form = QuestionLikeForm(request.POST)

    if not form.is_valid():
        return JsonResponse(
            {
                'ok': False,
                'error': 'invalid_data',
                'message': form.errors,
            },
            status=400,
        )

    question = form.question
    new_value = form.get_value()

    with transaction.atomic():
        like, created = QuestionLike.objects.get_or_create(
            user=request.user,
            question=question,
            defaults={
                'value': new_value,
            },
        )

        if created:
            delta = new_value
        elif like.value == new_value:
            delta = 0
        else:
            delta = new_value - like.value
            like.value = new_value
            like.save(update_fields=['value'])

        if delta:
            Question.objects.filter(id=question.id).update(
                rating=F('rating') + delta
            )

    question.refresh_from_db(fields=['rating'])

    return JsonResponse(
        {
            'ok': True,
            'rating': question.rating,
            'value': new_value,
        }
    )


@require_POST
def answer_like(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                'ok': False,
                'error': 'auth_required',
                'message': 'Войдите, чтобы оценивать ответы.',
            },
            status=401,
        )

    form = AnswerLikeForm(request.POST)

    if not form.is_valid():
        return JsonResponse(
            {
                'ok': False,
                'error': 'invalid_data',
                'message': form.errors,
            },
            status=400,
        )

    answer = form.answer
    new_value = form.get_value()

    with transaction.atomic():
        like, created = AnswerLike.objects.get_or_create(
            user=request.user,
            answer=answer,
            defaults={
                'value': new_value,
            },
        )

        if created:
            delta = new_value
        elif like.value == new_value:
            delta = 0
        else:
            delta = new_value - like.value
            like.value = new_value
            like.save(update_fields=['value'])

        if delta:
            Answer.objects.filter(id=answer.id).update(
                rating=F('rating') + delta
            )

    answer.refresh_from_db(fields=['rating'])

    return JsonResponse(
        {
            'ok': True,
            'rating': answer.rating,
            'value': new_value,
        }
    )


@require_POST
def mark_correct_answer(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                'ok': False,
                'error': 'auth_required',
                'message': 'Войдите, чтобы выбрать правильный ответ.',
            },
            status=401,
        )

    form = CorrectAnswerForm(request.POST)

    if not form.is_valid():
        return JsonResponse(
            {
                'ok': False,
                'error': 'invalid_data',
                'message': form.errors,
            },
            status=400,
        )

    question = form.question
    answer = form.answer

    if question.author_id != request.user.id:
        return JsonResponse(
            {
                'ok': False,
                'error': 'permission_denied',
                'message': 'Только автор вопроса может выбрать правильный ответ.',
            },
            status=403,
        )

    Answer.objects.filter(question=question).update(is_correct=False)

    answer.is_correct = True
    answer.save(update_fields=['is_correct', 'updated_at'])

    return JsonResponse(
        {
            'ok': True,
            'correct_answer_id': answer.id,
        }
    )