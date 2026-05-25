from pathlib import Path
from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models


def avatar_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()
    return f'avatars/{uuid4().hex}{extension}'


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь',
    )

    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
        verbose_name='Аватар',
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль #{self.pk} пользователя #{self.user_id}'