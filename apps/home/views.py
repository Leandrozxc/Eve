from django.shortcuts import render


def home_view(request):
    """
    Prototype home view.
    Simply renders the Home screen with placeholder feature previews.
    """
    return render(request, 'home/home.html')