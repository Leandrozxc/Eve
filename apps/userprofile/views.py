from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .models import Profile


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        bio = request.POST.get('bio', '').strip()

        profile.full_name = full_name
        profile.bio = bio
        profile.save()

        name_parts = full_name.split(maxsplit=1)
        request.user.first_name = name_parts[0] if name_parts else ''
        request.user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        request.user.save()

        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('userprofile:profile')

    memberships = request.user.company_memberships.select_related('company').all()

    context = {
        'profile': profile,
        'memberships': memberships,
    }
    return render(request, 'profile/profile.html', context)
