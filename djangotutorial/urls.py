from django.contrib import admin
from django.urls import include, path

urlpatters = [
	path("polls/", include("polls.urls")),
	path("admin/", admin.site.urls),
]