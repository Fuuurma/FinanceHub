from django.urls import path
from django.http import JsonResponse
from .api import api


def simple_health(request):
    return JsonResponse({"status": "ok", "message": "Server is running"})


urlpatterns = [
    path("health/", simple_health),
    path("", api.urls),
]
