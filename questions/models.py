from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count
from django.urls import reverse


class Tag(models.Model):
    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=64,
        unique=True,
        verbose_name='Слаг',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class QuestionQuerySet(models.QuerySet):
    def with_related(self):
        return (
            self
            .select_related('author')
            .prefetch_related('tags')
            .annotate(answers_count=Count('answers', distinct=True))
        )

    def new(self):
        return self.with_related().order_by('-created_at', '-id')

    def best(self):
        return self.with_related().order_by('-rating', '-created_at', '-id')

    def by_tag(self, tag_slug):
        return (
            self
            .with_related()
            .filter(tags__slug=tag_slug)
            .order_by('-created_at', '-id')
        )


class Question(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Автор',
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок',
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='questions',
        blank=True,
        verbose_name='Теги',
    )
    rating = models.IntegerField(
        default=0,
        verbose_name='Рейтинг',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
    )

    objects = QuestionQuerySet.as_manager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-created_at', '-id']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('questions:question', kwargs={'question_id': self.id})

    @property
    def likes(self):
        return self.rating


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Вопрос',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Текст ответа',
    )
    rating = models.IntegerField(
        default=0,
        verbose_name='Рейтинг',
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name='Правильный ответ',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f'Ответ #{self.id} на вопрос #{self.question_id}'

    @property
    def likes(self):
        return self.rating


class QuestionLike(models.Model):
    LIKE = 1
    DISLIKE = -1

    VALUE_CHOICES = (
        (LIKE, 'Лайк'),
        (DISLIKE, 'Дизлайк'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='question_likes',
        verbose_name='Пользователь',
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='question_likes',
        verbose_name='Вопрос',
    )
    value = models.SmallIntegerField(
        choices=VALUE_CHOICES,
        verbose_name='Оценка',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    class Meta:
        verbose_name = 'Лайк вопроса'
        verbose_name_plural = 'Лайки вопросов'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'question'],
                name='unique_question_like',
            )
        ]

    def __str__(self):
        return f'{self.user.username} → вопрос {self.question_id}: {self.value}'


class AnswerLike(models.Model):
    LIKE = 1
    DISLIKE = -1

    VALUE_CHOICES = (
        (LIKE, 'Лайк'),
        (DISLIKE, 'Дизлайк'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='answer_likes',
        verbose_name='Пользователь',
    )
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='answer_likes',
        verbose_name='Ответ',
    )
    value = models.SmallIntegerField(
        choices=VALUE_CHOICES,
        verbose_name='Оценка',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    class Meta:
        verbose_name = 'Лайк ответа'
        verbose_name_plural = 'Лайки ответов'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'answer'],
                name='unique_answer_like',
            )
        ]

    def __str__(self):
        return f'{self.user.username} → ответ {self.answer_id}: {self.value}'