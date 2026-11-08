from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        identifier = request.POST.get('email') or request.POST.get('username') or ''
        identifier = identifier.strip().lower()
        password = request.POST.get('password', '')

        if not identifier or not password:
            return render(
                request,
                'login/login.html',
                {
                    'error': 'Please provide both email/username and password.',
                    'email': identifier,
                },
            )

        user = authenticate(request, username=identifier, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('home:home')
        else:
            return render(
                request,
                'login/login.html',
                {
                    'error': 'Invalid email/username or password.',
                    'email': identifier,
                },
            )

    return render(request, 'login/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login:login')
