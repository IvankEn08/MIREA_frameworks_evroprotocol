from django.contrib import admin
from django.urls import include, path

from homepage.views import page_not_found


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("accidents/", include("accidents.urls")),
]

handler404 = page_not_found
