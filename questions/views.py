from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from questions.forms import AnswerForm, QuestionForm
from questions.models import Question, Tag
from questions.utils import paginate


def index(request):
    questions = Question.objects.new()
    page = paginate(questions, request, per_page=5)

    return render(
        request,
        'questions/index.html',
        {
            'questions': page.object_list,
            'page_obj': page,
        }
    )


def hot(request):
    questions = Question.objects.best()
    page = paginate(questions, request, per_page=5)

    return render(
        request,
        'questions/hot.html',
        {
            'questions': page.object_list,
            'page_obj': page,
        }
    )


def tag(request, tag_name):
    tag_obj = get_object_or_404(Tag, slug=tag_name)
    questions = Question.objects.by_tag(tag_name)
    page = paginate(questions, request, per_page=5)

    return render(
        request,
        'questions/tag.html',
        {
            'questions': page.object_list,
            'page_obj': page,
            'tag': tag_obj,
        }
    )


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
            return redirect(f'{question.get_absolute_url()}?page=1#answer-{answer.id}')
    else:
        form = AnswerForm()

    page = paginate(answers, request, per_page=5)

    return render(
        request,
        'questions/question.html',
        {
            'question': question,
            'answers': page.object_list,
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