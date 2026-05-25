from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from core.models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0
    verbose_name = 'Профиль'
    verbose_name_plural = 'Профиль'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'avatar')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)