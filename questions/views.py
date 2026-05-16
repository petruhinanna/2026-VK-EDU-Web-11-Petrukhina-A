from django.http import Http404
from django.shortcuts import render

from questions.utils import paginate


QUESTIONS = [
    {
        'id': i,
        'title': f'Question title {i}',
        'text': f'Text of question {i}. Пока это просто текст-заглушка для домашнего задания.',
        'likes': i * 2,
        'answers_count': i + 3,
        'tags': [
            'british-cats',
            'cats',
            'character',
            'python',
            'django',
            'perl',
            'TechnoPark',
            'MySQL',
            'Mail.Ru',
            'Voloshin',
            'Firefox',
        ],
    }
    for i in range(1, 20)
]


ANSWERS = [
    {
        'id': i,
        'text': f'Text of answer {i}. Пока это просто ответ-заглушка.',
        'likes': i,
        'is_correct': i == 1,
    }
    for i in range(1, 12)
]


def index(request):
    page = paginate(QUESTIONS, request, per_page=5)

    return render(
        request,
        'questions/index.html',
        context={
            'questions': page.object_list,
            'page_obj': page,
        }
    )


def hot(request):
    hot_questions = sorted(
        QUESTIONS,
        key=lambda question: question['likes'],
        reverse=True
    )

    page = paginate(hot_questions, request, per_page=5)

    return render(
        request,
        'questions/hot.html',
        context={
            'questions': page.object_list,
            'page_obj': page,
        }
    )


def tag(request, tag_name):
    tagged_questions = [
        question
        for question in QUESTIONS
        if tag_name in question['tags']
    ]

    page = paginate(tagged_questions, request, per_page=5)

    return render(
        request,
        'questions/tag.html',
        context={
            'questions': page.object_list,
            'page_obj': page,
            'tag_name': tag_name,
        }
    )


def question_detail(request, question_id):
    question = None

    for item in QUESTIONS:
        if item['id'] == question_id:
            question = item
            break

    if question is None:
        raise Http404('Question not found')

    page = paginate(ANSWERS, request, per_page=3)

    return render(
        request,
        'questions/question.html',
        context={
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