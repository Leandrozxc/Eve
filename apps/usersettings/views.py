from django.contrib import messages
from django.contrib.auth.decorators import login_required
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
