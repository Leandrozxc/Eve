from django.shortcuts import render, redirect


def login_view(request):
    if request.method == 'POST':
        return redirect('home:home')
    return render(request, 'login/login.html')