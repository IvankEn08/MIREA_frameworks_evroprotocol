from django.urls import path

from . import views


app_name = "accidents"

urlpatterns = [
    path("", views.accident_list, name="list"),
    path("search/", views.accident_search, name="search"),
    path("statistics/", views.statistics, name="statistics"),
    path("participants/", views.participant_list, name="participants"),
    path("<int:accident_id>/", views.accident_detail, name="detail"),
]
