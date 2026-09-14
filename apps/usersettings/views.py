from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import UserSettings


@login_required
def settings_view(request):
    settings, _ = UserSettings.objects.get_or_create(user=request.user)
    return render(request, 'usersettings/settings.html', {'settings': settings})