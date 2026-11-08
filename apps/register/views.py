from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render

from apps.events.models import Company, CompanyMember
from apps.userprofile.models import Profile
from apps.usersettings.models import UserSettings


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        company_name = request.POST.get('company', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not full_name or not email or not company_name or not password:
            return render(
                request,
                'register/register.html',
                {
                    'error': 'Please complete all required fields.',
                    'full_name': full_name,
                    'email': email,
                    'company': company_name,
                },
            )

        if password != confirm_password:
            return render(
                request,
                'register/register.html',
                {
                    'error': 'Passwords do not match.',
                    'full_name': full_name,
                    'email': email,
                    'company': company_name,
                },
            )

        if User.objects.filter(username=email).exists():
            return render(
                request,
                'register/register.html',
                {
                    'error': 'An account with this email already exists.',
                    'full_name': full_name,
                    'company': company_name,
                },
            )

        name_parts = full_name.split(maxsplit=1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )
                Profile.objects.create(user=user, full_name=full_name)
                UserSettings.objects.create(user=user)

                company, _ = Company.objects.get_or_create(name=company_name)
                CompanyMember.objects.create(company=company, user=user, role="OWNER")

        except IntegrityError:
            return render(
                request,
                'register/register.html',
                {
                    'error': 'Could not create account. Please try again.',
                    'full_name': full_name,
                    'company': company_name,
                },
            )

        messages.success(request, 'Registration successful! You may now log in.')
        return redirect('login:login')

    return render(request, 'register/register.html')
