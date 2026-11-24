"""Маршруты помещений."""

from django.urls import path

from rooms import views

app_name = "rooms"

urlpatterns = [
    path("", views.rooms, name="list"),
    path("available/", views.available_rooms, name="available"),
    path("create/", views.room_create, name="create"),
    path("<slug:slug>/edit/", views.room_update, name="edit"),
    path("<slug:slug>/", views.room_detail, name="detail"),
]
