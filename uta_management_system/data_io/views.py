import pandas as pd
import datetime
from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.permissions import  IsAdminUser
from .models import *
from .serializers import *

# Create your views here.
class DataIOViewSet(viewsets.ModelViewSet):
    """
    Viewset to modify the schedule link and return timesheet
    """
    permission_classes = (IsAdminUser,)
    queryset = DataIO.objects.all()
    serializer_class = DataIOSerializer

    def get_schedules(self, link:str) -> bool:
        """
        Populate the database with UTA and Shift information
        """
        #  Read the csv file from link
        if "docs.google.com" in link:
            link = link.replace('/edit?usp=sharing', '/export?format=csv&gid=0')
        try:
            df = pd.read_csv(link)
        except Exception:
            return False
        # Add UTAs to database
        uta_names = [name.split() for name in df.iloc[:,0].to_list()]
        emplid = df.iloc[:,1].to_list()
        uta_dict = {emplid[i]:uta_names[i] for i in range(len(emplid))}
        for empl,name in uta_dict.items():
            try:
                UTA.objects.get(lastname=name[1], firstname=name[0], emplid=empl)
            except UTA.DoesNotExist:
                new_uta = UTA.objects.create(lastname=name[1], firstname=name[0], emplid=empl)
                new_uta.save()
        # Add shifts to database
        DAYS = {
            'M': 'Monday',
            'Tu': 'Tuesday',
            'W': 'Wednesday',
            'Th': 'Thursday',
            'F': 'Friday'
        }
        for s in df.columns[2:]:
            shift = s.split()
            if shift[0].strip() not in DAYS.keys():
                break
            on_shift = df.loc[df[s]==1.0].iloc[:,1].to_list()
            day = DAYS[f'{shift[0].strip()}']
            start = datetime.time(int(shift[1][:2]), int(shift[1][3:]), 0)
            end = datetime.time(int(shift[3][:2]), int(shift[3][3:]), 0)
            try:
                new_shift = Shift.objects.get(description=s.strip(), day=day, start=start, end=end)
            except Shift.DoesNotExist:
                new_shift = Shift.objects.create(description=s.strip(), day=day, start=start, end=end)
                new_shift.save()
            
            for empl in on_shift:    
                uta = UTA.objects.get(emplid=empl)
                uta.shifts.add(new_shift)

        return True

    def create(self, request):
        """
        Add or update the link to UTA schedule
        """
        new_link = request.data
        DataIO.objects.all().delete()
        Shift.objects.all().delete()
        UTA.objects.all().delete()
        success = self.get_schedules(new_link['file_link'])
        if not success:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        new_entry = DataIO.objects.create(file_link=new_link['file_link'])
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
