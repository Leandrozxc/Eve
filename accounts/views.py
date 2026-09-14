from django.contrib import messages
from django.shortcuts import redirect, render


# def login_view(request):
#     """
#     Prototype login view.
#     GET  -> show the login form.
#     POST -> skip real authentication and go straight to Home.
#     """
#     if request.method == 'POST':
#         return redirect('home:home')
#     return render(request, 'login/login.html')


def register_view(request):
    """
    Prototype register view.
    GET  -> show the registration form.
    POST -> skip database saving, show a success message, redirect to Login.
    """
    if request.method == 'POST':
        messages.success(request, 'Registration successful! You may now log in.')
        return redirect('accounts:login')
    return render(request, 'register/register.html')


def logout_view(request):
    """
    Prototype logout view.
    Simply redirects back to the Login screen.
    """
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')