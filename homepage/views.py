from django.shortcuts import render
from django.db.models import Count, Q

from accidents.models import Accident


def index(request):
    statistics = Accident.objects.aggregate(
        total=Count("id"),
        emergencies=Count("id", filter=Q(has_injured=True) | Q(has_fire=True)),
        closed=Count("id", filter=Q(status=Accident.STATUS_CLOSED)),
    )
    context = {
        "statistics": statistics,
        "recent_accidents": Accident.objects.annotate(
            participant_count=Count("participants", distinct=True)
        ).order_by("-occurred_at", "-id")[:3],
    }
    return render(request, "homepage/index.html", context)


def page_not_found(request, exception):
    return render(request, "404.html", status=404)
