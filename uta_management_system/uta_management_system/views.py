import requests
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView

from data_io.models import UTA


def homepage(request):
    """
    Render homepage.html in default endpoint
    """
    return render(request, "homepage.html")


class Checkin(APIView):
    # extra_fields = ("alternate-toggle",)
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "checkin.html"

    def get(self, request, random_pass):
        new_pass = requests.post(
            request.build_absolute_uri(reverse("dataio:random_pass-list")), json={}
        ).json()["random_pass"]
        if random_pass == new_pass:
            return render(request, "checkin.html")
        return render(request, "homepage.html")

    def post(self, request, random_pass):
        new_pass = requests.post(
            request.build_absolute_uri(reverse("dataio:random_pass-list")), json={}
        ).json()["random_pass"]

        if random_pass != new_pass:
            return render(request, "homepage.html")

        absent_uta = request.POST.get("fullname", None)
        if absent_uta:
            response = requests.post(
                request.build_absolute_uri(reverse("dataio:checkin-list")),
                json={
                    "emplid": UTA.objects.get(fullname=absent_uta).emplid,
                    "number_of_shifts": request.data["number_of_shifts"],
                    "alternate_day": request.data["alternate_day"],
                    "covered_by": request.data["covered_by"],
                },
            )
        else:
            response = requests.post(
                request.build_absolute_uri(reverse("dataio:checkin-list")),
                json={
                    "emplid": request.data["emplid"],
                    "number_of_shifts": request.data["number_of_shifts"],
                    "alternate_day": request.data["alternate_day"],
                },
            )

        if response.status_code == 303:
            on_shift = response.json()["on_shift"].split(",")
            return render(
                request,
                "checkin.html",
                {
                    "on_shift": on_shift,
                    "covering": request.data["emplid"],
                    "shift_num": request.data["number_of_shifts"],
                    "alt_day": request.data["alternate_day"],
                },
            )

        if response.status_code == 201:
            messages.success(request, response.json()["message"])
        else:
            messages.error(request, response.json()["failure"])

        return HttpResponseRedirect(self.request.path_info)


class AdminActions(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "admin_actions.html"

    def get(self, request):
        random_pass = requests.post(
            request.build_absolute_uri(reverse("dataio:random_pass-list")), json={}
        ).json()["random_pass"]
        return render(request, "admin_actions.html", {"random_pass": random_pass})

    def post(self, request):
        response = requests.post(
            request.build_absolute_uri(reverse("dataio:update_schedule-list")),
            json={"file_link": request.data["file_link"]},
        )
        if response.status_code == 201:
            messages.success(request, "Schedules updated successfully!")
        else:
            messages.error(
                request,
                "Failed to update schedule. Make sure the link is valid and csv is formatted appropriately.",
            )
        return HttpResponseRedirect(self.request.path_info)
