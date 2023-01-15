"""
Define, specify and update REST Api operations' behaviors
"""
import hashlib
from datetime import datetime, time

import pandas as pd
from rest_framework import status, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import *
from .serializers import *


# Create your views here.
class DataIOViewSet(viewsets.ModelViewSet):
    """
    Viewset for DataIO model
    """

    queryset = DataIO.objects.all()
    serializer_class = DataIOSerializer

    def get_schedules(self, link: str) -> bool:
        """
        Populate the database with `UTA` and `Shift` information from the given `link`

        Args:
            link: `str` object representing a link with google sheet or csv file
        Returns:
            `True` if successfully read data from the given `link`, otherwise returns `False`
        """
        #  if provided link is a google sheet, export the sheet as csv
        if "docs.google.com/spreadsheets" in link:
            link = link.replace("/edit?usp=sharing", "/export?format=csv&gid=0")
        # Read a dataframe from `link`, return False if the read operation fails
        try:
            df = pd.read_csv(link)
        except Exception:
            return False

        # Add UTAs to database from the dataframe `df`
        uta_names = df.iloc[:, 0].to_list()  # get UTA names from Col 1
        emplid = df.iloc[:, 1].to_list()  # get UTA emplids from Col 2
        # <emplid: name> mapping for all the UTAs
        uta_dict = {emplid[i]: uta_names[i] for i in range(len(emplid))}
        # iterate through the `uta_dict` dictionary and create a new UTA with the emplid and name if the UTA doesn't already exist in the database
        for empl, name in uta_dict.items():
            try:
                UTA.objects.get(fullname=name, emplid=empl)
            except UTA.DoesNotExist:
                new_uta = UTA.objects.create(fullname=name, emplid=empl)
                new_uta.save()

        # Dictionary used to get days based on the letters representing that day in the shifts schedule
        DAYS = {
            "M": "Monday",
            "Tu": "Tuesday",
            "W": "Wednesday",
            "Th": "Thursday",
            "F": "Friday",
        }
        # iterate through the column names that contains shifts information (starting from column 2)
        for s in df.columns[2:]:
            # parse the column name (e.g. M 11:30 - 13:00)
            shift = s.split()  # ["M", "11:30", "-", "13:00"]
            # break out of the loop stop reading shift informations if the column name is not a shift description
            if shift[0].strip() not in DAYS.keys():
                break

            # get the name of the UTA's who are on shift for this particular shift
            on_shift = (
                df.loc[df[s] == 1.0].iloc[:, 1].to_list()
            )  # UTA names in the rows with a 1 are considered to be on shift
            day = DAYS[
                f"{shift[0].strip()}"
            ]  # use `DAYS` dictionary to get the day from parsed shift information
            # create `time` objects for the start time and end time from parsed shift information
            start = time(int(shift[1][:2]), int(shift[1][3:]), 0)
            end = time(int(shift[3][:2]), int(shift[3][3:]), 0)
            # try to create and add a new `Shift` object if the shift doesn't exist in the database already
            try:
                new_shift = Shift.objects.get(
                    description=s.strip(), day=day, start=start, end=end
                )
            except Shift.DoesNotExist:
                new_shift = Shift.objects.create(
                    description=s.strip(), day=day, start=start, end=end
                )
                new_shift.save()
            # add the `Shift` object to `UTA` objects for the utas who are `on_shift`
            for empl in on_shift:
                uta = UTA.objects.get(emplid=empl)
                uta.shifts.add(new_shift)

        return True  # return True indicating that the Shift objects and UTA objects were read successfully

    def create(self, request):
        """
        1. Replace the `file_link` with the provided new link if the new link is successfully read by pandas
        2. Delete all the `UTA` and `Shift` information in the database and repopulate the database with information from the new link
        """
        # get the `old_link` from the database if the old link exists
        old_link = DataIO.objects.all()[0].file_link if DataIO.objects.all() else ""
        # get the `new_link` from POST request
        new_link = request.data
        # delete all Shift, UTA and DataIO objects from the database
        DataIO.objects.all().delete()
        Shift.objects.all().delete()
        UTA.objects.all().delete()
        # try to read the schedule from the `new_link`
        success = self.get_schedules(new_link["file_link"])
        # if the schedule is not read successfully from the new link, repopulate the database with the UTA and Shift information of the `old_link`
        if not success:
            DataIO.objects.create(file_link=old_link)
            self.get_schedules(old_link)
            return Response(
                {"Failure": "unable to parse csv file in given link"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        # if the read operation was successful, add the `new_link` to the database and save it
        new_entry = DataIO.objects.create(file_link=new_link["file_link"])
        new_entry.save()
        return Response(status=status.HTTP_201_CREATED)


class ShiftViewSet(viewsets.ModelViewSet):
    """
    Viewset for `Shift` model
    """

    permission_classes = (IsAdminUser,)
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer


class UTAViewSet(viewsets.ModelViewSet):
    """
    Viewset for `UTA` model
    """

    permission_classes = (IsAdminUser,)
    queryset = UTA.objects.all()
    serializer_class = UTASerializer


class RandomPassViewSet(viewsets.ModelViewSet):
    """
    Viewset for `RandomPass` model
    """

    queryset = RandomPass.objects.all()
    http_method_names = ["post"]
    serializer_class = RandomPassSerializer

    def create(self, request=None):
        """
        Deletes the old `random_pass` and generates a new one
        """
        serializer = RandomPassSerializer
        # use current date and additional string to generate an md5 hash
        time_str = f"{datetime.now().date().strftime('%m/%d/%Y')}RyanSadabUmarYoomin"
        time_str = hashlib.md5(time_str.encode()).hexdigest()[:10]
        add_cases = ""
        # alternate between uppercase and lowercase letters if applicable
        for i in range(len(time_str)):
            add_cases += (
                time_str[i].upper()
                if (time_str[i].isalpha() and i % 2 == 0)
                else time_str[i]
            )
        time_str = add_cases
        # delete old `random_pass` and add the new `random_pass`
        RandomPass.objects.all().delete()
        new_pass = RandomPass.objects.create(random_pass=time_str)
        return Response(serializer(new_pass).data, status=status.HTTP_201_CREATED)


class CheckinViewSet(viewsets.ModelViewSet):
    """
    Viewset for `Checkin` model
    """

    queryset = Checkin.objects.all()
    serializer_class = CheckinSerializer

    def get_next_shift(self, shift: Shift, num: int) -> list[Shift]:
        """
        Retrieves `num` number of Shift objects that start immediately after the given `shift`

        Args:
            shift: a `Shift` object
            num: `int` representing how many shifts to get
        Returns:
            `list` of `Shift` objects
        """
        # get the day of `shift`
        day = shift.day
        # return empty list if `num` is less than or equal to 1
        if num - 1 <= 0:
            return []
        # get all the shifts from database that are on the same day as `shift`
        shifts = list(Shift.objects.filter(day=(day,)))
        # sort the retrieved shifts based on the start time
        shifts.sort(key=lambda x: x.start)
        # return empty list if no shifts are acquired from the database
        if not shifts:
            return []
        # get the index of shift in the list of shifts retrieved from the database
        index = shifts.index(shift)
        # get `num` number of shifts starting from `index` in the retrieved list and append them to an empty list
        result = []
        for i in range(1, num + 1):
            # return shifts obtained so far if adding num exceeds the length of the retrieved list
            if index + i > len(shifts) - 1:
                return result
            result.append(shifts[index + i])
        # return the shifts list
        return result

    def get_current_shift(self, day=None) -> tuple[Shift, int]:
        """
        Retrieves a `Shift` that is happening at the current time. Calculate how many minutes have passed since the start of the retrieved `Shift` object.

        Args:
            day: used if provided to get the shift on that particular `day`
        Returns:
            `tuple` of a `Shift` object and an `int`
        """
        # get the current day if day parameter is None
        now = datetime.now().time()
        if not day:
            day = datetime.now().strftime("%A")
        # initialize variables that will be returned
        current_shift, late = None, 0
        # iterate through the shifts that are occuring on given `day`
        for shift in Shift.objects.filter(day=day):
            # if the current time is between the `start` time and the `end` time of the `shift`
            if shift.start < now < shift.end:
                # get the `current_shift` and determing how `late` the `current_time` is from the shift `start` time
                current_shift = shift
                late = (
                    int(
                        (
                            datetime.combine(datetime.today(), now)
                            - datetime.combine(datetime.today(), shift.start)
                        ).total_seconds()
                    )
                    // 60
                )
        # return the `current_shift` and `late` minutes
        return (current_shift, late)

    def create(self, request):
        """
        Checkin a `UTA` to a `Shift` by creating a `Checkin` object if the following conditions are met:
        1. The given emplid belongs to a `UTA`
        2. There is a `Shift` at the current time and day (or given alternate day)
        3. The `Shift` is assigned to the `UTA` with given emplid or the UTA is being covered by another UTA
        """
        # check if the given emplid belongs to a `UTA`, return 404 response if it doesn't
        empl = request.data["emplid"]
        try:
            uta = UTA.objects.get(emplid=empl)
        except UTA.DoesNotExist:
            return Response(
                {"failure": "you're not a UTA"}, status=status.HTTP_404_NOT_FOUND
            )
        # get the current shift (pass `alternate_day` which can be empty)
        shift = self.get_current_shift(request.data["alternate_day"])
        # get the additional shifts to be checked in for from the request (defaults to 0)
        num_of_shifts = (
            request.data["number_of_shifts"] if request.data["number_of_shifts"] else 0
        )
        # return 403 response if shift[0] object is None (no shift at current time)
        if not shift[0]:
            return Response(
                {"failure": "No shift at current time"},
                status=status.HTTP_403_FORBIDDEN,
            )
        # get the next shifts based on `num_of_shifts`
        next_shifts = self.get_next_shift(shift[0], int(num_of_shifts))

        # if the UTA is extremely late to their shift, return 403 response and prevent them from checking in
        # UTA is extremely late if they missed 1/3 of their shift
        if shift[1] > (
            (
                datetime.combine(datetime.today(), shift[0].end)
                - datetime.combine(datetime.today(), shift[0].start)
            ).total_seconds()
            // 180
        ):
            return Response(
                {"failure": "You're extremely late to your shift"},
                status=status.HTTP_403_FORBIDDEN,
            )
        # if check if there is a `covered_by` field in the request
        covered_by = request.data.get("covered_by", "")

        # if `covered_by` field is empty and the UTA is not on shift, return 303 response with list of UTA names who are currently on shift
        if shift[0] not in list(uta.shifts.all()) and not covered_by:
            on_shift = ",".join(
                [
                    uta.fullname
                    for uta in (list(UTA.objects.filter(shifts__id=shift[0].pk)))
                ]
            )
            # the 303 response is handled by frontend to allow covering shifts
            return Response({"on_shift": on_shift}, status=status.HTTP_303_SEE_OTHER)

        # create a new `Checkin` object with all the information if the `Checkin` object doesn't already exist in the database
        try:
            new_checkin = Checkin.objects.get(
                emplid=empl, shift=shift[0], covered_by=covered_by
            )
        except Checkin.DoesNotExist:
            new_checkin = Checkin.objects.create(
                emplid=empl, shift=shift[0], late_mins=shift[1], covered_by=covered_by
            )
            new_checkin.save()

        # checkin for the additional shifts and keep track of how many shifts have been checked in
        count = 1
        for s in next_shifts:
            # only checkin if it hasn't been done already
            try:
                next_shift_checkin = Checkin.objects.get(
                    emplid=empl, shift=s, covered_by=covered_by
                )
            except Checkin.DoesNotExist:
                #  stop checking in if the `UTA`` is not on any of the additional shifts
                if s not in list(uta.shifts.all()):
                    break
                next_shift_checkin = Checkin.objects.create(
                    emplid=empl, shift=s, covered_by=covered_by
                )
                next_shift_checkin.save()
                count += 1

        # return 201 response indicating a successful checkin
        return Response(
            {"message": f"Checked in successfully for {count} shift(s)"},
            status=status.HTTP_201_CREATED,
        )
