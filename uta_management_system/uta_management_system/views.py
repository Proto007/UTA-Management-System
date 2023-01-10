import requests
from django.shortcuts import render
from django.urls import reverse
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView


def homepage(request):
    """
    Render homepage.html in default endpoint
    """
    return render(request, "homepage.html")


def checkin(request, random_pass):
    response = requests.post(
        request.build_absolute_uri(reverse("dataio:random_pass-list")), json={}
    )
    data = response.json()
    new_pass = data["random_pass"]
    if random_pass == new_pass:
        return render(request, "checkin.html")
    return render(request, "homepage.html")


class AdminActions(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "admin_actions.html"

    def get(self, request):
        random_pass = requests.post(
            request.build_absolute_uri(reverse("dataio:random_pass-list")), json={}
        ).json()["random_pass"]
        return render(request, "admin_actions.html", {"random_pass": random_pass})

    def post(self, request):
        random_pass = requests.post(
            request.build_absolute_uri(reverse("dataio:random_pass-list")), json={}
        ).json()["random_pass"]

        response = requests.post(
            request.build_absolute_uri(reverse("dataio:update_schedule-list")),
            json={"file_link": request.data["file_link"]},
        )

        success = False
        if response.status_code == 201:
            success = True

        return render(
            request,
            "admin_actions.html",
            {"updated": success, "random_pass": random_pass},
        )
