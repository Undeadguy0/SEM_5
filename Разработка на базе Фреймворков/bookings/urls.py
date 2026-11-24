"""Маршруты бронирований."""

from django.urls import path

from bookings import views

app_name = "bookings"

urlpatterns = [
    path("", views.bookings, name="bookings"),
    path("statistics/", views.statistics, name="statistics"),
    path("create/", views.booking_create, name="booking_create"),
    path(
        "<int:booking_id>/edit/",
        views.booking_update,
        name="booking_update",
    ),
    path(
        "<int:booking_id>/cancel/",
        views.booking_cancel,
        name="booking_cancel",
    ),
    path("<int:booking_id>/", views.booking_detail, name="detail"),
]
