from django.contrib import admin
from django.db.models import Count

from questions.models import (
    Answer,
    AnswerLike,
    Question,
    QuestionLike,
    Tag,
)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ('author', 'text', 'rating', 'is_correct', 'created_at')
    readonly_fields = ('created_at',)
    raw_id_fields = ('author',)
    show_change_link = True


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'author',
        'rating',
        'answers_count_admin',
        'created_at',
    )
    search_fields = (
        'title',
        'text',
        'author__username',
        'tags__name',
    )
    list_filter = (
        'created_at',
        'tags',
    )
    raw_id_fields = (
        'author',
        'tags',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    inlines = (AnswerInline,)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related('author')
            .prefetch_related('tags')
            .annotate(answers_count_value=Count('answers', distinct=True))
        )

    @admin.display(description='Ответов')
    def answers_count_admin(self, obj):
        return obj.answers_count_value


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'question',
        'author',
        'rating',
        'is_correct',
        'created_at',
    )
    search_fields = (
        'text',
        'question__title',
        'author__username',
    )
    list_filter = (
        'is_correct',
        'created_at',
    )
    raw_id_fields = (
        'question',
        'author',
    )
    readonly_fields = (
        'created_at',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('question', 'author')


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'question',
        'value',
        'created_at',
    )
    search_fields = (
        'user__username',
        'question__title',
    )
    list_filter = (
        'value',
        'created_at',
    )
    raw_id_fields = (
        'user',
        'question',
    )
    readonly_fields = (
        'created_at',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'question')


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'answer',
        'value',
        'created_at',
    )
    search_fields = (
        'user__username',
        'answer__text',
    )
    list_filter = (
        'value',
        'created_at',
    )
    raw_id_fields = (
        'user',
        'answer',
    )
    readonly_fields = (
        'created_at',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'answer')


admin.site.site_header = 'Поясняем на котятах'
admin.site.site_title = 'Поясняем на котятах'
admin.site.index_title = 'Администрирование сайта'