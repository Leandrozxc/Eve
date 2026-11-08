from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    # Event routes
    path("", views.event_list, name="event_list"),
    path("create/", views.event_create, name="event_create"),
    path("<int:event_id>/", views.event_detail, name="event_detail"),
    path("<int:event_id>/edit/", views.event_edit, name="event_edit"),
    path("<int:event_id>/delete/", views.event_delete, name="event_delete"),
    path("<int:event_id>/status/", views.event_update_status, name="event_update_status"),
    path("<int:event_id>/assign/", views.assignment_create, name="assignment_create"),
    path("assignments/<int:assignment_id>/update/", views.assignment_update, name="assignment_update"),
    path("assignments/<int:assignment_id>/delete/", views.assignment_delete, name="assignment_delete"),

    # Company & Role routes
    path("companies/", views.company_list, name="company_list"),
    path("companies/create/", views.company_create, name="company_create"),
    path("companies/<int:company_id>/join/", views.company_join, name="company_join"),
    path("companies/<int:company_id>/members/", views.company_members, name="company_members"),
]
