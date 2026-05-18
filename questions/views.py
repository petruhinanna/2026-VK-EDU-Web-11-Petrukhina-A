from django.shortcuts import get_object_or_404, render

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
        .select_related('author')
        .order_by('-created_at', '-id')
    )

    page = paginate(answers, request, per_page=5)

    return render(
        request,
        'questions/question.html',
        {
            'question': question,
            'answers': page.object_list,
            'page_obj': page,
        }
    )


def ask(request):
    return render(
        request,
        'questions/ask.html'
    )