from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import redirect, render


def register_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        company = request.POST.get('company', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not full_name or not email or not company or not password:
            return render(
                request,
                'register/register.html',
                {'error': 'Please complete all required fields.'},
            )

        if password != confirm_password:
            return render(
                request,
                'register/register.html',
                {'error': 'Passwords do not match.'},
            )

        if User.objects.filter(username=email).exists():
            return render(
                request,
                'register/register.html',
                {'error': 'An account with this email already exists. Please use another email.'},
            )

        name_parts = full_name.split(maxsplit=1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        try:
            User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
        except IntegrityError:
            return render(
                request,
                'register/register.html',
                {'error': 'An account with this email already exists. Please use another email.'},
            )

        return redirect('login:login')

    return render(request, 'register/register.html')