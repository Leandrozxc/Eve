from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def home_view(request):
    """
    Home view protected by login requirement.
    Renders the Home screen for authenticated users.
    """
    return render(request, 'home/home.html')