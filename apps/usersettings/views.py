import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from .models import UserSettings


@login_required
def settings_view(request):
    settings, _ = UserSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        dark_mode = request.POST.get('dark_mode') == 'on'
        email_notifications = request.POST.get('email_notifications') == 'on'

        settings.dark_mode = dark_mode
        settings.email_notifications = email_notifications
        settings.save()

        messages.success(request, 'Your settings have been saved!')
        return redirect('usersettings:settings')

    return render(request, 'usersettings/settings.html', {'settings': settings})


@login_required
def toggle_theme_view(request):
    """Instant theme toggle endpoint for seamless dark/light mode switching."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    settings, _ = UserSettings.objects.get_or_create(user=request.user)

    # Allow explicit mode or toggle current state
    try:
        body = json.loads(request.body) if request.body else {}
    except (ValueError, TypeError):
        body = {}

    theme = body.get('theme') or request.POST.get('theme')

    if theme == 'dark':
        settings.dark_mode = True
    elif theme == 'light':
        settings.dark_mode = False
    else:
        settings.dark_mode = not settings.dark_mode

    settings.save(update_fields=['dark_mode'])

    return JsonResponse({
        'status': 'ok',
        'dark_mode': settings.dark_mode,
        'theme': 'dark' if settings.dark_mode else 'light',
    })
