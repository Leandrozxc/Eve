from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include('apps.login.urls')),
    path('register/', include('apps.register.urls')),
    path('profile/', include('apps.userprofile.urls')),
    path('settings/', include('apps.usersettings.urls')),
    path('home/', include('apps.home.urls')),
    path('', RedirectView.as_view(pattern_name='login:login', permanent=False)),
    path('events/', include('apps.events.urls')),   
]
