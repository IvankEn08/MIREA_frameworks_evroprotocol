from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Case, CharField, Count, Q, Value, When
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    AccidentFilterForm,
    AccidentForm,
    AccidentPhotoForm,
    ParticipantEntryForm,
)
from .models import Accident, EmergencyMessage, Participant, Vehicle


def accident_list(request):
    filter_form = AccidentFilterForm(request.GET or None)
    accidents = Accident.objects.annotate(
        participant_count=Count("participants", distinct=True),
        severity_label=Case(
            When(
                Q(has_injured=True) | Q(has_fire=True),
                then=Value("Повышенная опасность"),
            ),
            default=Value("Без пострадавших"),
            output_field=CharField(),
        ),
    )
    if filter_form.is_valid():
        severity = filter_form.cleaned_data["severity"]
        location = filter_form.cleaned_data["location"]
        status = filter_form.cleaned_data["status"]
        if severity == "emergency":
            accidents = accidents.filter(Q(has_injured=True) | Q(has_fire=True))
        elif severity == "regular":
            accidents = accidents.filter(has_injured=False, has_fire=False)
        elif severity == "injured":
            accidents = accidents.filter(has_injured=True)
        elif severity == "fire":
            accidents = accidents.filter(has_fire=True)
        if location:
            accidents = accidents.filter(location__icontains=location)
        if status:
            accidents = accidents.filter(status=status)
    page_obj = Paginator(accidents.order_by("-occurred_at", "-id"), 9).get_page(
        request.GET.get("page")
    )
    query_params = request.GET.copy()
    query_params.pop("page", None)
    return render(
        request,
        "accidents/accident_list.html",
        {
            "accidents": page_obj.object_list,
            "page_obj": page_obj,
            "filter_form": filter_form,
            "query_params": query_params.urlencode(),
        },
    )


def accident_detail(request, accident_id):
    accident = (
        Accident.objects.annotate(
            participant_count=Count("participants", distinct=True)
        )
        .prefetch_related("participants__vehicle", "messages", "photos")
        .filter(pk=accident_id)
        .first()
    )
    if accident is None:
        raise Http404("ДТП не найдено")
    return render(
        request,
        "accidents/accident_detail.html",
        {
            "accident": accident,
            "participant_form": ParticipantEntryForm(),
            "photo_form": AccidentPhotoForm(),
        },
    )


def accident_search(request):
    filter_form = AccidentFilterForm(request.GET or None)
    accidents = Accident.objects.none()
    if filter_form.is_valid() and request.GET:
        severity = filter_form.cleaned_data["severity"]
        location = filter_form.cleaned_data["location"]
        status = filter_form.cleaned_data["status"]
        accidents = Accident.objects.all()
        if severity == "emergency":
            accidents = accidents.filter(Q(has_injured=True) | Q(has_fire=True))
        elif severity == "regular":
            accidents = accidents.filter(has_injured=False, has_fire=False)
        elif severity == "injured":
            accidents = accidents.filter(has_injured=True)
        elif severity == "fire":
            accidents = accidents.filter(has_fire=True)
        if location:
            accidents = accidents.filter(location__icontains=location)
        if status:
            accidents = accidents.filter(status=status)
        accidents = accidents.order_by("-occurred_at", "-id")
    return render(
        request,
        "accidents/accident_search.html",
        {
            "accidents": accidents,
            "filter_form": filter_form,
            "searched": bool(request.GET),
        },
    )


def accident_create(request):
    form = AccidentForm(request.POST if request.method == "POST" else None)
    photo_form = AccidentPhotoForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
    )
    if request.method == "POST" and form.is_valid() and photo_form.is_valid():
        with transaction.atomic():
            accident = form.save()
            photo = photo_form.save(commit=False)
            photo.accident = accident
            if photo.image:
                photo.save()
        messages.success(request, f"ДТП №{accident.pk} зарегистрировано.")
        return redirect("accidents:detail", accident_id=accident.pk)
    return render(
        request,
        "accidents/accident_form.html",
        {"form": form, "photo_form": photo_form, "mode": "create"},
    )


def accident_edit(request, accident_id):
    accident = get_object_or_404(Accident, pk=accident_id)
    form = AccidentForm(
        request.POST if request.method == "POST" else None,
        instance=accident,
    )
    photo_form = AccidentPhotoForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
    )
    if request.method == "POST" and form.is_valid() and photo_form.is_valid():
        with transaction.atomic():
            updated_accident = form.save()
            photo = photo_form.save(commit=False)
            photo.accident = updated_accident
            if photo.image:
                photo.save()
        messages.success(request, f"Сведения о ДТП №{accident.pk} обновлены.")
        return redirect("accidents:detail", accident_id=accident.pk)
    return render(
        request,
        "accidents/accident_form.html",
        {"form": form, "photo_form": photo_form, "mode": "edit", "accident": accident},
    )


def participant_add(request, accident_id):
    accident = get_object_or_404(Accident, pk=accident_id)
    form = ParticipantEntryForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            data = form.cleaned_data
            vehicle = Vehicle.objects.filter(
                plate_number__iexact=data["plate_number"]
            ).first()
            if vehicle is None:
                vehicle = Vehicle.objects.create(
                    plate_number=data["plate_number"],
                    brand=data["brand"],
                    model=data["vehicle_model"],
                )
            Participant.objects.create(
                accident=accident,
                vehicle=vehicle,
                full_name=data["full_name"],
                phone=data["phone"],
            )
        messages.success(request, "Участник и его автомобиль добавлены в карточку ДТП.")
        return redirect("accidents:detail", accident_id=accident.pk)
    return render(
        request,
        "accidents/participant_form.html",
        {"form": form, "accident": accident},
    )


def accident_photo_add(request, accident_id):
    accident = get_object_or_404(Accident, pk=accident_id)
    form = AccidentPhotoForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
    )
    if request.method == "POST" and form.is_valid():
        if not form.cleaned_data["image"]:
            form.add_error("image", "Выберите изображение для загрузки.")
            return render(
                request,
                "accidents/photo_form.html",
                {"form": form, "accident": accident},
            )
        photo = form.save(commit=False)
        photo.accident = accident
        photo.save()
        messages.success(request, "Фотография добавлена к материалам ДТП.")
        return redirect("accidents:detail", accident_id=accident.pk)
    return render(
        request,
        "accidents/photo_form.html",
        {"form": form, "accident": accident},
    )


@require_POST
def accident_cancel(request, accident_id):
    accident = get_object_or_404(Accident, pk=accident_id)
    if accident.status != Accident.STATUS_CANCELLED:
        accident.status = Accident.STATUS_CANCELLED
        accident.save(update_fields=["status"])
        messages.success(
            request,
            f"Регистрация ДТП №{accident.pk} отменена. Запись сохранена в журнале.",
        )
    return redirect("accidents:list")


def participant_list(request):
    participants = Participant.objects.select_related("accident", "vehicle").order_by(
        "-accident__occurred_at", "full_name"
    )
    return render(
        request,
        "accidents/participant_list.html",
        {"participants": participants},
    )


def statistics(request):
    category_expression = Case(
        When(
            Q(has_injured=True) | Q(has_fire=True),
            then=Value("Повышенная опасность"),
        ),
        default=Value("Без пострадавших"),
        output_field=CharField(),
    )
    by_category = (
        Accident.objects.annotate(category=category_expression)
        .values("category")
        .annotate(accident_count=Count("id"))
        .order_by("-accident_count", "category")
    )
    by_location = (
        Accident.objects.values("location")
        .annotate(accident_count=Count("id"))
        .filter(accident_count__gte=1)
        .order_by("-accident_count", "location")
    )
    totals = Accident.objects.aggregate(
        total=Count("id"),
        emergencies=Count("id", filter=Q(has_injured=True) | Q(has_fire=True)),
        closed=Count("id", filter=Q(status=Accident.STATUS_CLOSED)),
    )
    messages_by_service = (
        EmergencyMessage.objects.values("service_name")
        .annotate(message_count=Count("id"))
        .order_by("-message_count", "service_name")
    )
    context = {
        "by_category": by_category,
        "by_location": by_location,
        "totals": totals,
        "messages_by_service": messages_by_service,
    }
    return render(request, "accidents/statistics.html", context)
