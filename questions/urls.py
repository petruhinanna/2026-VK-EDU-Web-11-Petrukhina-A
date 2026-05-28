from django.urls import path

from questions import views

app_name = 'questions'

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question_detail, name='question'),
    path('ask/', views.ask, name='ask'),

    path('ajax/question-like/', views.question_like, name='question_like'),
    path('ajax/answer-like/', views.answer_like, name='answer_like'),
    path('ajax/correct-answer/', views.mark_correct_answer, name='correct_answer'),
    path('ajax/search/', views.search_suggestions, name='search_suggestions'),
]