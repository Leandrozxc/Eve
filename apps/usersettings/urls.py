from django.urls import path
from . import views

app_name = 'usersettings'

urlpatterns = [
    path('', views.settings_view, name='settings'),
    path('toggle-theme/', views.toggle_theme_view, name='toggle_theme'),
]
