"""Страницы бронирований."""

from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Avg
from django.db.models import Count
from django.db.models import F
from django.db.models import Max
from django.db.models import Q
from django.http import Http404
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from bookings.models import Booking
from homepage.views import http_not_found
from rooms.models import Room
from users.models import User


SORT_FIELDS = {
    "date": "booking_date",
    "room": "room__name",
    "user": "user__name",
}
PAGE_SIZE = 5


def bookings(request: HttpRequest) -> HttpResponse:
    """Показать активные бронирования с фильтрами и страницами."""
    booking_date = request.GET.get("date", "").strip()
    room_id = request.GET.get("room", "").strip()
    user_id = request.GET.get("user", "").strip()
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "date")
    error = None
    if sort not in SORT_FIELDS:
        sort = "date"

    bookings_data = Booking.objects.filter(is_cancelled=False)
    if booking_date:
        try:
            selected_date = datetime.strptime(
                booking_date,
                "%Y-%m-%d",
            ).date()
        except ValueError:
            error = "Укажите корректную дату."
        else:
            bookings_data = bookings_data.filter(
                booking_date=selected_date,
            )
    if room_id.isdigit():
        bookings_data = bookings_data.filter(room_id=int(room_id))
    if user_id.isdigit():
        bookings_data = bookings_data.filter(user_id=int(user_id))
    if query:
        bookings_data = bookings_data.filter(topic__icontains=query)

    bookings_data = bookings_data.annotate(
        room_name=F("room__name"),
        capacity=F("room__capacity"),
        user_name=F("user__name"),
    ).order_by(SORT_FIELDS[sort], "id")
    bookings_data = bookings_data.values(
        "id",
        "booking_date",
        "start_time",
        "end_time",
        "topic",
        "is_cancelled",
        "room_name",
        "capacity",
        "user_name",
    )
    paginator = Paginator(bookings_data, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "bookings": page_obj,
        "page_obj": page_obj,
        "booking_date": booking_date,
        "selected_room": room_id,
        "selected_user": user_id,
        "query": query,
        "sort": sort,
        "rooms": Room.objects.order_by("name"),
        "users": User.objects.order_by("name"),
        "error": error,
    }
    return render(request, "bookings/booking_list.html", context)


def booking_detail(
    request: HttpRequest,
    booking_id: int,
) -> HttpResponse:
    """Показать карточку одного бронирования."""
    try:
        booking = get_object_or_404(
            Booking.objects.select_related("room", "user"),
            pk=booking_id,
        )
    except Http404:
        return http_not_found(
            request,
            "Бронирование не найдено.",
            "bookings:bookings",
            "К списку бронирований",
        )
    context = {"booking": booking}
    return render(request, "bookings/booking_detail.html", context)


def statistics(request: HttpRequest) -> HttpResponse:
    """Показать сводку, группировки и помещения с несколькими бронями."""
    bookings_count = Booking.objects.filter(is_cancelled=False).count()
    summary = Room.objects.aggregate(
        rooms_count=Count("id"),
        average_capacity=Avg("capacity"),
        max_capacity=Max("capacity"),
    )
    by_room = Room.objects.annotate(
        bookings_count=Count(
            "bookings",
            filter=Q(bookings__is_cancelled=False),
        ),
        room_name=F("name"),
    ).values(
        "room_name",
        "bookings_count",
    ).order_by("-bookings_count", "room_name")
    popular = by_room.filter(bookings_count__gt=1)
    by_user = User.objects.annotate(
        bookings_count=Count(
            "bookings",
            filter=Q(bookings__is_cancelled=False),
        ),
        user_name=F("name"),
    ).values(
        "user_name",
        "bookings_count",
    ).order_by("-bookings_count", "user_name")
    context = {
        "bookings_count": bookings_count,
        "summary": summary,
        "statistics": by_room,
        "by_user": by_user,
        "popular": popular,
        "users": User.objects.order_by("name"),
    }
    return render(request, "bookings/statistics.html", context)
