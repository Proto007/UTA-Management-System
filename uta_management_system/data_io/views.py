import hashlib
from datetime import datetime, time

import pandas as pd
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import *
from .serializers import *


# Create your views here.
class DataIOViewSet(viewsets.ModelViewSet):
    """
    Viewset to modify the schedule link and return timesheet
    """

    queryset = DataIO.objects.all()
    serializer_class = DataIOSerializer

    def get_schedules(self, link: str) -> bool:
        """
        Populate the database with UTA and Shift information
        """
        #  Read the csv file from link
        if "docs.google.com" in link:
            link = link.replace("/edit?usp=sharing", "/export?format=csv&gid=0")
        try:
            df = pd.read_csv(link)
        except Exception:
            return False
        # Add UTAs to database
        uta_names = [name.split() for name in df.iloc[:, 0].to_list()]
        emplid = df.iloc[:, 1].to_list()
        uta_dict = {emplid[i]: uta_names[i] for i in range(len(emplid))}
        for empl, name in uta_dict.items():
            try:
                UTA.objects.get(lastname=name[1], firstname=name[0], emplid=empl)
            except UTA.DoesNotExist:
                new_uta = UTA.objects.create(
                    lastname=name[1], firstname=name[0], emplid=empl
                )
                new_uta.save()
        # Add shifts to database
        DAYS = {
            "M": "Monday",
            "Tu": "Tuesday",
            "W": "Wednesday",
            "Th": "Thursday",
            "F": "Friday",
        }
        for s in df.columns[2:]:
            shift = s.split()
            if shift[0].strip() not in DAYS.keys():
                break
            on_shift = df.loc[df[s] == 1.0].iloc[:, 1].to_list()
            day = DAYS[f"{shift[0].strip()}"]
            start = time(int(shift[1][:2]), int(shift[1][3:]), 0)
            end = time(int(shift[3][:2]), int(shift[3][3:]), 0)
            try:
                new_shift = Shift.objects.get(
                    description=s.strip(), day=day, start=start, end=end
                )
            except Shift.DoesNotExist:
                new_shift = Shift.objects.create(
                    description=s.strip(), day=day, start=start, end=end
                )
                new_shift.save()

            for empl in on_shift:
                uta = UTA.objects.get(emplid=empl)
                uta.shifts.add(new_shift)

        return True

    def create(self, request):
        """
        Add or update the link to UTA schedule
        """
        old_link = DataIO.objects.all()[0].file_link if DataIO.objects.all() else ""
        new_link = request.data
        DataIO.objects.all().delete()
        Shift.objects.all().delete()
        UTA.objects.all().delete()
        success = self.get_schedules(new_link["file_link"])
        if not success:
            DataIO.objects.create(file_link=old_link)
            self.get_schedules(old_link)
            return Response(
                {"Failure": "unable to parse csv file in given link"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        new_entry = DataIO.objects.create(file_link=new_link["file_link"])
        new_entry.save()
        return Response(status=status.HTTP_201_CREATED)


class ShiftViewSet(viewsets.ModelViewSet):
    """
    Viewset to represent a single shift
    """

    permission_classes = (IsAdminUser,)
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer


class UTAViewSet(viewsets.ModelViewSet):
    """
    Viewset to represent a single UTA
    """

    permission_classes = (IsAdminUser,)
    queryset = UTA.objects.all()
    serializer_class = UTASerializer


class RandomPassViewSet(viewsets.ModelViewSet):
    queryset = RandomPass.objects.all()
    http_method_names = ["post"]
    serializer_class = RandomPassSerializer

    def create(self, request=None):
        serializer = RandomPassSerializer
        time_str = f"{datetime.now().date().strftime('%m/%d/%Y')}RyanSadabUmarYoomin"
        time_str = hashlib.md5(time_str.encode()).hexdigest()[:10]
        add_cases = ""
        for i in range(len(time_str)):
            add_cases += (
                time_str[i].upper()
                if (time_str[i].isalpha() and i % 2 == 0)
                else time_str[i]
            )
        time_str = add_cases
        RandomPass.objects.all().delete()
        new_pass = RandomPass.objects.create(random_pass=time_str)
        return Response(serializer(new_pass).data, status=status.HTTP_201_CREATED)


class CheckinViewSet(viewsets.ModelViewSet):
    queryset = Checkin.objects.all()
    serializer_class = CheckinSerializer

    def get_next_shift(self, shift: Shift, num: int):
        now = datetime.now().time()
        day = now.strftime("%A")

        if num - 1 <= 0:
            return []

        shifts = list(Shift.objects.filter(day=(day,)))
        shifts.sort(key=lambda x: x.start)
        if not shifts:
            return []

        index = shifts.index(shift)
        result = []
        for i in range(num):
            if index + i > len(shifts) - 1:
                return result
            result.append(shifts[index + i])
        return result

    def get_current_shift(self, day=None):
        now = datetime.now().time()
        if not day:
            day = datetime.now().strftime("%A")
        current_shift = None
        late = 0
        for shift in Shift.objects.filter(day=day):
            if shift.start < now < shift.end:
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
        return (current_shift, late)

    def create(self, request):
        # check if UTA exists on database
        empl = request.data["emplid"]
        try:
            uta = UTA.objects.get(emplid=empl)
        except UTA.DoesNotExist:
            return Response(
                {"failure": "you're not a UTA"}, status=status.HTTP_404_NOT_FOUND
            )

        # get the shift in current time
        shift = self.get_current_shift(request.data["alternate_day"])
        num_of_shifts = (
            request.data["number_of_shifts"] if request.data["number_of_shifts"] else 1
        )
        next_shifts = self.get_next_shift(shift, int(num_of_shifts))

        if not shift[0]:
            return Response(
                {"failure": "No shift at current time"},
                status=status.HTTP_403_FORBIDDEN,
            )

        #  check if UTA is on shift
        if shift[0] not in list(uta.shifts.all()):
            return Response(
                {"failure": "Covering another UTA?"}, status=status.HTTP_403_FORBIDDEN
            )

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

        try:
            new_checkin = Checkin.objects.get(emplid=empl, shift=shift[0])
        except Checkin.DoesNotExist:
            new_checkin = Checkin.objects.create(
                emplid=empl, shift=shift[0], late_mins=shift[1]
            )
            new_checkin.save()
        count = 1
        for s in next_shifts:
            try:
                next_shift_checkin = Checkin.objects.get(emplid=empl, shift=s)
            except Checkin.DoesNotExist:
                #  check if UTA is on shift
                if s not in list(uta.shifts.all()):
                    break
                next_shift_checkin = Checkin.objects.create(emplid=empl, shift=s)
                next_shift_checkin.save()
                count += 1

        return Response(
            {"message": f"Checked in successfully for {count} shifts"},
            status=status.HTTP_200_OK,
        )
