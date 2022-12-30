from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'data_io',DataIOViewSet,basename="data_io")
router.register(r'random_pass',RandomPassViewSet,basename="random_pass")

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
