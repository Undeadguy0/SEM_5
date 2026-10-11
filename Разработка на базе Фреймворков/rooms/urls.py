"""Маршруты помещений."""

from django.urls import path

from rooms import views

urlpatterns = [
    path("", views.rooms, name="rooms"),
    path("<int:room_id>/", views.room_detail, name="room_detail"),
]
