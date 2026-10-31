from django.shortcuts import render

from db.queries import get_dashboard_statistics, get_recent_accidents


def index(request):
    context = {
        "statistics": get_dashboard_statistics(),
        "recent_accidents": get_recent_accidents(limit=3),
    }
    return render(request, "homepage/index.html", context)


def page_not_found(request, exception):
    return render(request, "404.html", status=404)
