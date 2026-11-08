from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path("joins/", views.join_demo, name="join_demo"),
]