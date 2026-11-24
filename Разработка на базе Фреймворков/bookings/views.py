"""Страницы бронирований."""

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
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from bookings.forms import BookingFilterForm
from bookings.forms import BookingForm
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
OCCUPIED_MESSAGE = (
    "Выбранное помещение уже забронировано на эту дату."
)


def bookings(request: HttpRequest) -> HttpResponse:
    """Показать бронирования с фильтрами и страницами."""
    if request.GET:
        submitted = request.GET.copy()
        if not submitted.get("status"):
            submitted["status"] = "active"
        if not submitted.get("sort"):
            submitted["sort"] = "date"
        form = BookingFilterForm(submitted)
    else:
        form = BookingFilterForm()

    error = ""
    booking_date = None
    room_id = None
    user_id = None
    query = ""
    sort = "date"
    status = "active"
    form_valid = form.is_bound and form.is_valid()
    if form_valid:
        booking_date = form.cleaned_data.get("date")
        room = form.cleaned_data.get("room")
        selected_user = form.cleaned_data.get("user")
        room_id = room.pk if room else None
        user_id = selected_user.pk if selected_user else None
        query = (form.cleaned_data.get("q") or "").strip()
        sort = form.cleaned_data.get("sort") or "date"
        status = form.cleaned_data.get("status") or "active"
    elif form.is_bound:
        error = "Проверьте корректность параметров фильтрации."

    if status == "cancelled":
        bookings_data = Booking.objects.cancelled()
    elif status == "completed":
        bookings_data = Booking.objects.completed()
    else:
        bookings_data = Booking.objects.active()
        status = "active"
    if sort not in SORT_FIELDS:
        sort = "date"
    if form_valid:
        if booking_date:
            bookings_data = bookings_data.for_date(booking_date)
        if room_id:
            bookings_data = bookings_data.filter(room_id=room_id)
        if user_id:
            bookings_data = bookings_data.filter(user_id=user_id)
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
        "status",
        "room_name",
        "capacity",
        "user_name",
    )
    paginator = Paginator(bookings_data, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "bookings": page_obj,
        "page_obj": page_obj,
        "form": form,
        "query": query,
        "sort": sort,
        "status": status,
        "error": error,
    }
    return render(request, "bookings/booking_list.html", context)


def _missing_booking(request: HttpRequest) -> HttpResponse:
    """Вернуть страницу 404 для отсутствующей активной брони."""
    return http_not_found(
        request,
        "Бронирование не найдено.",
        "bookings:bookings",
        "К списку бронирований",
    )


def booking_create(request: HttpRequest) -> HttpResponse:
    """Создать бронирование из ModelForm."""
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            room = form.cleaned_data["room"]
            booking_date = form.cleaned_data["booking_date"]
            is_booked = (
                Booking.objects.active()
                .filter(room=room, booking_date=booking_date)
                .exists()
            )
            if is_booked:
                form.add_error(None, OCCUPIED_MESSAGE)
            else:
                form.save()
                return redirect("bookings:bookings")
    else:
        form = BookingForm(
            initial={"booking_date": timezone.localdate()},
        )
    return render(
        request,
        "bookings/booking_form.html",
        {"form": form},
    )


def booking_update(
    request: HttpRequest,
    booking_id: int,
) -> HttpResponse:
    """Изменить активное бронирование."""
    try:
        booking = get_object_or_404(
            Booking.objects.active(),
            pk=booking_id,
        )
    except Http404:
        return _missing_booking(request)
    if request.method == "POST":
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            room = form.cleaned_data["room"]
            booking_date = form.cleaned_data["booking_date"]
            is_booked = (
                Booking.objects.active()
                .filter(room=room, booking_date=booking_date)
                .exclude(pk=booking.pk)
                .exists()
            )
            if is_booked:
                form.add_error(None, OCCUPIED_MESSAGE)
            else:
                form.save()
                return redirect("bookings:bookings")
    else:
        form = BookingForm(instance=booking)
    context = {"form": form, "booking": booking}
    return render(request, "bookings/booking_form.html", context)


@require_POST
def booking_cancel(
    request: HttpRequest,
    booking_id: int,
) -> HttpResponse:
    """Отменить активное бронирование, не удаляя запись."""
    try:
        booking = get_object_or_404(
            Booking.objects.active(),
            pk=booking_id,
        )
    except Http404:
        return _missing_booking(request)
    booking.cancel()
    return redirect("bookings:bookings")


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
    """Показать сводку по статусам, помещениям и организаторам."""
    status_stats = Booking.objects.aggregate(
        total_bookings=Count("id"),
        active_bookings=Count(
            "id",
            filter=Q(status=Booking.Status.ACTIVE),
        ),
        cancelled_bookings=Count(
            "id",
            filter=Q(status=Booking.Status.CANCELLED),
        ),
        completed_bookings=Count(
            "id",
            filter=Q(status=Booking.Status.COMPLETED),
        ),
    )
    summary = Room.objects.aggregate(
        rooms_count=Count("id"),
        average_capacity=Avg("capacity"),
        max_capacity=Max("capacity"),
    )
    by_room = Room.objects.annotate(
        bookings_count=Count(
            "bookings",
            filter=Q(bookings__status=Booking.Status.ACTIVE),
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
            filter=Q(bookings__status=Booking.Status.ACTIVE),
        ),
        user_name=F("name"),
    ).values(
        "user_name",
        "bookings_count",
    ).order_by("-bookings_count", "user_name")
    context = {
        "status_stats": status_stats,
        "summary": summary,
        "statistics": by_room,
        "by_user": by_user,
        "popular": popular,
        "users": User.objects.order_by("name"),
    }
    return render(request, "bookings/statistics.html", context)
