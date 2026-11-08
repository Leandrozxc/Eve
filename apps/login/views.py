from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import redirect, render


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')

    next_url = request.GET.get('next') or request.POST.get('next') or ''

    if request.method == 'POST':
        identifier = request.POST.get('email') or request.POST.get('username') or ''
        identifier = identifier.strip()
        password = request.POST.get('password', '')

        if not identifier or not password:
            return render(
                request,
                'login/login.html',
                {
                    'error': 'Please provide both email/username and password.',
                    'email': identifier,
                    'next': next_url,
                },
            )

        # Look up user by username or email (case-insensitive)
        matched_user = User.objects.filter(
            Q(username__iexact=identifier) | Q(email__iexact=identifier)
        ).first()

        user = None
        if matched_user:
            user = authenticate(request, username=matched_user.username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('home:home')
        else:
            return render(
                request,
                'login/login.html',
                {
                    'error': 'Invalid email/username or password.',
                    'email': identifier,
                    'next': next_url,
                },
            )

    return render(request, 'login/login.html', {'next': next_url})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login:login')
