from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Profile


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profile/profile.html', {'profile': profile})