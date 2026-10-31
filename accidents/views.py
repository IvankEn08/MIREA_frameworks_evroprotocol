from django.http import Http404
from django.shortcuts import render

from db.queries import (
    get_accident,
    get_accidents,
    get_accidents_by_severity,
    get_participants_with_accidents,
    get_statistics_by_category,
    get_statistics_by_location,
)


def accident_list(request):
    return render(
        request,
        "accidents/accident_list.html",
        {"accidents": get_accidents()},
    )


def accident_detail(request, accident_id):
    accident = get_accident(accident_id)
    if accident is None:
        raise Http404("ДТП не найдено")
    return render(
        request,
        "accidents/accident_detail.html",
        {"accident": accident},
    )


def accident_search(request):
    severity = request.GET.get("severity", "")
    accidents = get_accidents_by_severity(severity) if severity else []
    return render(
        request,
        "accidents/accident_search.html",
        {"accidents": accidents, "severity": severity},
    )


def participant_list(request):
    return render(
        request,
        "accidents/participant_list.html",
        {"participants": get_participants_with_accidents()},
    )


def statistics(request):
    context = {
        "by_category": get_statistics_by_category(),
        "by_location": get_statistics_by_location(),
    }
    return render(request, "accidents/statistics.html", context)
