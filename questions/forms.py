from django import forms
from django.db import transaction

from questions.models import (
    Answer,
    AnswerLike,
    Question,
    QuestionLike,
    Tag,
)


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        label='Теги',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'например: django, python, коты',
            'class': 'form_input',
        }),
    )

    class Meta:
        model = Question
        fields = ('title', 'text')
        labels = {
            'title': 'Заголовок',
            'text': 'Текст',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Введите заголовок вопроса',
                'class': 'form_input',
            }),
            'text': forms.Textarea(attrs={
                'rows': 8,
                'placeholder': 'Опишите вопрос подробнее',
                'class': 'form_input',
            }),
        }

    def __init__(self, *args, author=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.author = author

    def clean_title(self):
        title = self.cleaned_data['title'].strip()

        if len(title) < 5:
            raise forms.ValidationError('Заголовок должен быть не короче 5 символов.')

        return title

    def clean_text(self):
        text = self.cleaned_data['text'].strip()

        if len(text) < 10:
            raise forms.ValidationError('Текст вопроса должен быть не короче 10 символов.')

        return text

    def clean_tags(self):
        raw_tags = self.cleaned_data.get('tags', '')

        tag_names = [
            tag.strip()
            for tag in raw_tags.split(',')
            if tag.strip()
        ]

        unique_tag_names = []

        for tag_name in tag_names:
            if tag_name.lower() not in [item.lower() for item in unique_tag_names]:
                unique_tag_names.append(tag_name)

        if len(unique_tag_names) > 5:
            raise forms.ValidationError('Можно указать не больше 5 тегов.')

        for tag_name in unique_tag_names:
            if len(tag_name) > 64:
                raise forms.ValidationError('Длина одного тега не должна превышать 64 символа.')

        return unique_tag_names

    @transaction.atomic
    def save(self, commit=True):
        question = super().save(commit=False)
        question.author = self.author

        if commit:
            question.save()

            for tag_name in self.cleaned_data['tags']:
                slug = tag_name.lower().replace(' ', '-')

                tag, _ = Tag.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'name': tag_name,
                    },
                )

                question.tags.add(tag)

        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        labels = {
            'text': 'Ваш ответ',
        }
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Введите ваш ответ...',
                'class': 'form_input',
            }),
        }

    def __init__(self, *args, author=None, question=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.author = author
        self.question = question

    def clean_text(self):
        text = self.cleaned_data['text'].strip()

        if len(text) < 5:
            raise forms.ValidationError('Ответ должен быть не короче 5 символов.')

        return text

    def save(self, commit=True):
        answer = super().save(commit=False)
        answer.author = self.author
        answer.question = self.question

        if commit:
            answer.save()

        return answer


class QuestionLikeForm(forms.Form):
    question_id = forms.IntegerField()
    value = forms.ChoiceField(
        choices=(
            ('like', 'like'),
            ('dislike', 'dislike'),
        )
    )

    def clean_question_id(self):
        question_id = self.cleaned_data['question_id']

        try:
            self.question = Question.objects.active().get(id=question_id)
        except Question.DoesNotExist:
            raise forms.ValidationError('Вопрос не найден.')

        return question_id

    def get_value(self):
        if self.cleaned_data['value'] == 'like':
            return QuestionLike.LIKE

        return QuestionLike.DISLIKE


class AnswerLikeForm(forms.Form):
    answer_id = forms.IntegerField()
    value = forms.ChoiceField(
        choices=(
            ('like', 'like'),
            ('dislike', 'dislike'),
        )
    )

    def clean_answer_id(self):
        answer_id = self.cleaned_data['answer_id']

        try:
            self.answer = Answer.objects.active().get(id=answer_id)
        except Answer.DoesNotExist:
            raise forms.ValidationError('Ответ не найден.')

        return answer_id

    def get_value(self):
        if self.cleaned_data['value'] == 'like':
            return AnswerLike.LIKE

        return AnswerLike.DISLIKE


class CorrectAnswerForm(forms.Form):
    question_id = forms.IntegerField()
    answer_id = forms.IntegerField()

    def clean(self):
        cleaned_data = super().clean()

        question_id = cleaned_data.get('question_id')
        answer_id = cleaned_data.get('answer_id')

        if not question_id or not answer_id:
            return cleaned_data

        try:
            self.question = Question.objects.active().get(id=question_id)
        except Question.DoesNotExist:
            raise forms.ValidationError('Вопрос не найден.')

        try:
            self.answer = Answer.objects.active().get(
                id=answer_id,
                question=self.question,
            )
        except Answer.DoesNotExist:
            raise forms.ValidationError('Ответ не найден.')

        return cleaned_data