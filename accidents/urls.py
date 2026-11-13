from django.urls import path

from . import views


app_name = "accidents"

urlpatterns = [
    path("", views.accident_list, name="list"),
    path("create/", views.accident_create, name="create"),
    path("search/", views.accident_search, name="search"),
    path("statistics/", views.statistics, name="statistics"),
    path("participants/", views.participant_list, name="participants"),
    path("<int:accident_id>/edit/", views.accident_edit, name="edit"),
    path("<int:accident_id>/cancel/", views.accident_cancel, name="cancel"),
    path(
        "<int:accident_id>/participants/add/",
        views.participant_add,
        name="participant_add",
    ),
    path("<int:accident_id>/photos/add/", views.accident_photo_add, name="photo_add"),
    path("<int:accident_id>/", views.accident_detail, name="detail"),
]
