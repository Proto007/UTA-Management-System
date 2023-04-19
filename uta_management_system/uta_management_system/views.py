from datetime import datetime, timedelta

import requests
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
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
    """
    Handle requests from `checkin` template
    """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "checkin.html"

    def get(self, request, random_pass):
        # get the current randompass from `dataio` app's `random_pass` api
        new_pass = requests.post(
            request.build_absolute_uri(reverse("dataio:random_pass-list")), json={}
        ).json()["random_pass"]
        # render `checkin.html` page if the endpoint matches the `random_pass`
        if random_pass == new_pass:
            return render(request, "checkin.html")
        # render `homepage.html` if the endpoint is invalid
        return render(request, "homepage.html")

    def post(self, request, random_pass):
        # check if the post request came from `random_pass` endpoint
        new_pass = requests.post(
            request.build_absolute_uri(reverse("dataio:random_pass-list")), json={}
        ).json()["random_pass"]
        # render `homepage.html` if the endpoint is invalid
        if random_pass != new_pass:
            return render(request, "homepage.html")
        # check if the post request has a `fullname` field
        absent_uta = request.POST.get("fullname", None)
        
        # use 0 if the number_of_shifts field is left blank
        additional_shifts = request.POST.get("number_of_shifts", None)
        if not additional_shifts:
            additional_shifts = 0

        # if request contains `fullname` field, make post request to `dataio` app's `checkin` model
        # the post request is being made for a UTA who is getting covered by another UTA
        if absent_uta:
            alt_day = request.POST.get("alternate_day", None)
            if not alt_day:
                alt_day = ""

            response = requests.post(
                request.build_absolute_uri(reverse("dataio:checkin-list")),
                json={
                    "emplid": UTA.objects.get(fullname=absent_uta).emplid,
                    "number_of_shifts": int(additional_shifts),
                    "alternate_day": alt_day,
                    "covered_by": request.data["covered_by"],
                },
            )
        # if request doesn't contain `fullname`, make a post request without assuming that the UTA will get covered
        else:
            response = requests.post(
                request.build_absolute_uri(reverse("dataio:checkin-list")),
                json={
                    "emplid": request.data["emplid"],
                    "number_of_shifts": int(additional_shifts),
                    "alternate_day": request.data["alternate_day"],
                },
            )
        # if the response code for post request is 303, the UTA with given emplid is absent
        if response.status_code == 303:
            # get the names of the UTAs who are currently on shift
            on_shift = response.json()["on_shift"].split(",")
            # render `checkin.html` with some contexts which will allow the UTA to cover another UTA's shift
            return render(
                request,
                "checkin.html",
                {
                    "on_shift": on_shift,
                    "covering": request.data["emplid"],
                    "shift_num": int(additional_shifts),
                    "alt_day": request.data["alternate_day"],
                },
            )
        # add messages for success or failure of the post request indicating success or failure of the checkin attempt
        if response.status_code == 201:
            messages.success(request, response.json()["message"])
        else:
            print(response.json().keys())
            messages.error(request, response.json()["failure"])
        # redirect to the current endpoint (shows messages)
        return HttpResponseRedirect(self.request.path_info)


class AdminActions(APIView):
    """
    Handle requests from `adminpage` template
    """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "adminpage.html"

    def get(self, request):
        # get the `random_pass` from `dataio` app's `random_pass` model through a Post request
        random_pass = requests.post(
            request.build_absolute_uri(reverse("dataio:random_pass-list")), json={}
        ).json()["random_pass"]
        # render `adminpage.html` by providing `random_pass` as context
        return render(request, "adminpage.html", {"random_pass": random_pass})

    def post(self, request):
        # if the post request is being made to `dataio:timesheet` api
        if request.data.get("timesheet", ""):
            # convert `start_date` given in the request into a datetime object
            start_date = datetime.strptime(request.data["start_date"], "%Y-%m-%d")
            # convert `weeks` given in the request into an integer
            weeks = int(request.data["weeks"])

            # calculate the end_date (`weeks` number of Fridays away from the `start_date`)
            end_date = start_date
            while True:
                if end_date.weekday() == 4:
                    weeks -= 1
                if weeks == 0:
                    break
                end_date += timedelta(days=1)

            # get the timesheets zip file from `dataio:timesheet` api via Post request
            response = requests.post(
                request.build_absolute_uri(reverse("dataio:timesheet-list")),
                json={
                    "start_date": start_date.isoformat(sep="T"),
                    "end_date": end_date.isoformat(sep="T"),
                },
            )
            # allow the user to download the zip file as 'timesheets.zip'
            response = HttpResponse(response, content_type="application/force-download")
            response["Content-Disposition"] = "attachment; filename=timesheets.zip"
            return response

        # following code only gets executed if the post request is being made to change the `file_link`
        # update schedules, uta info, schedule `file_link` by making a Post request to `dataio:update_schedule`
        response = requests.post(
            request.build_absolute_uri(reverse("dataio:update_schedule-list")),
            json={"file_link": request.data["file_link"]},
        )
        # add messages indicating success/failure of the Post request
        if response.status_code == 201:
            messages.success(request, "Schedules updated successfully!")
        else:
            messages.error(
                request,
                "Failed to update schedule. Make sure the link is valid and csv is formatted appropriately.",
            )
        # redirect to the current endpoint (showing messages)
        return HttpResponseRedirect(self.request.path_info)
