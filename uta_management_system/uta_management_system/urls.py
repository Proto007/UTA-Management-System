"""uta_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path

from . import views

# assign endpoints to different views and apps
urlpatterns = [
    re_path("^$", views.homepage),
    path(
        "6d975d9e9f5e6d5a461ded16097ec288/",
        views.AdminActions.as_view(),
        name="admin_actions",
    ),
    path("admin/", admin.site.urls),
    path("api/", include("data_io.urls")),
    path("<str:random_pass>/", views.Checkin.as_view(), name="checkin"),
]
