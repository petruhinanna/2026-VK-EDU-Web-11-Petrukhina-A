from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from core.forms import LoginForm, ProfileForm, SignupForm
from core.models import Profile


def get_safe_next_url(request, default_url_name='questions:index'):
    next_url = (
        request.POST.get('next')
        or request.GET.get('next')
        or request.META.get('HTTP_REFERER')
    )

    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url

    return reverse(default_url_name)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('questions:index')

    next_url = get_safe_next_url(request)

    if request.method == 'POST':
        form = LoginForm(request.POST, request=request)

        if form.is_valid():
            login(request, form.get_user())
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(
        request,
        'core/login.html',
        {
            'form': form,
            'next': next_url,
        }
    )


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('questions:index')

    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('questions:index')
    else:
        form = SignupForm()

    return render(
        request,
        'core/signup.html',
        {
            'form': form,
        }
    )


def logout_view(request):
    next_url = get_safe_next_url(request)

    logout(request)

    return redirect(next_url)


@login_required(login_url='core:login')
def profile_view(request):
    Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(
            request.POST,
            request.FILES,
            user=request.user,
        )

        if form.is_valid():
            form.save()
            return redirect('core:profile')
    else:
        form = ProfileForm(user=request.user)

    return render(
        request,
        'core/profile.html',
        {
            'form': form,
        }
    )