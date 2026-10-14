"""Маршруты бронирований."""

from django.urls import path

from bookings import views

app_name = "bookings"

urlpatterns = [
    path("", views.bookings, name="bookings"),
    path("<int:booking_id>/", views.booking_detail, name="detail"),
]
