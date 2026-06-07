from pathlib import Path

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from core.models import Profile


User = get_user_model()

MAX_AVATAR_SIZE = 2 * 1024 * 1024
ALLOWED_AVATAR_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите логин',
            'class': 'form_input',
        })
    )

    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите пароль',
            'class': 'form_input',
        })
    )

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            self.user = authenticate(
                self.request,
                username=username,
                password=password,
            )

            if self.user is None:
                raise forms.ValidationError('Неверный логин или пароль.')

        return cleaned_data

    def get_user(self):
        return self.user


class SignupForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите логин',
            'class': 'form_input',
        })
    )

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Введите email',
            'class': 'form_input',
        })
    )

    first_name = forms.CharField(
        label='Имя',
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите имя',
            'class': 'form_input',
        })
    )

    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите пароль',
            'class': 'form_input',
        })
    )

    password_repeat = forms.CharField(
        label='Повтор пароля',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Повторите пароль',
            'class': 'form_input',
        })
    )

    def clean_username(self):
        username = self.cleaned_data['username']

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует.')

        return username

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')

        return email

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')

        if password and password_repeat and password != password_repeat:
            self.add_error('password_repeat', 'Пароли не совпадают.')

        if password:
            try:
                validate_password(password)
            except ValidationError as error:
                self.add_error('password', error)

        return cleaned_data

    def save(self):
        with transaction.atomic():
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password'],
                first_name=self.cleaned_data['first_name'],
            )

            Profile.objects.get_or_create(user=user)

        return user


class ProfileForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите логин',
            'class': 'form_input',
        })
    )

    email = forms.EmailField(
        label='Email',
        required=False,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Введите email',
            'class': 'form_input',
        })
    )

    avatar = forms.ImageField(
        label='Аватар',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form_input',
        })
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if user is not None:
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email

    def clean_username(self):
        username = self.cleaned_data['username']

        if User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует.')

        return username

    def clean_email(self):
        email = self.cleaned_data['email']

        if (
            email
            and User.objects.filter(email=email).exclude(pk=self.user.pk).exists()
        ):
            raise forms.ValidationError('Пользователь с таким email уже существует.')

        return email

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')

        if not avatar:
            return avatar

        extension = Path(avatar.name).suffix.lower()

        if extension not in ALLOWED_AVATAR_EXTENSIONS:
            raise forms.ValidationError(
                'Можно загрузить только изображения JPG, PNG, GIF или WEBP.'
            )

        if avatar.size > MAX_AVATAR_SIZE:
            raise forms.ValidationError(
                'Размер аватарки не должен превышать 2 МБ.'
            )

        return avatar

    def save(self):
        user = self.user

        with transaction.atomic():
            user.username = self.cleaned_data['username']
            user.email = self.cleaned_data['email']
            user.save()

            profile, _ = Profile.objects.get_or_create(user=user)

            avatar = self.cleaned_data.get('avatar')
            if avatar:
                profile.avatar = avatar
                profile.save()

        return user