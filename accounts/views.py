from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect


def logout_view(request):
    """
    Logs out the authenticated user, clears their session, and redirects to Login.
    """
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('login:login')