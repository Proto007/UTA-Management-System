from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *

app_name = "dataio"
# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r"update_schedule", DataIOViewSet, basename="update_schedule")
router.register(
    r"6d975d9e9f5e6d5a461ded16097ec288", RandomPassViewSet, basename="random_pass"
)
router.register(r"checkin", CheckinViewSet, basename="checkin")

# The API URLs are now determined automatically by the router
urlpatterns = [
    path("", include(router.urls)),
]
