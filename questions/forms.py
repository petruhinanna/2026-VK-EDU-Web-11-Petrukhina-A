from django import forms
from django.db import transaction

from questions.models import Answer, Question, Tag


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