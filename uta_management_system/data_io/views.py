from django.shortcuts import render
from .models import DataIO
from rest_framework import viewsets,status
from rest_framework.response import Response
from .serializers import DataIOSerializer

# Create your views here.
class DataIOViewSet(viewsets.ModelViewSet):
    """
    Viewset to modify the schedule link and return timesheet
    """
    queryset = DataIO.objects.all()
    serializer_class = DataIOSerializer
    def create(self, request):
        """
        Add or update the link to UTA schedule
        """
        new_link = request.data
        DataIO.objects.all().delete()
        new_entry = DataIO.objects.create(file_link=new_link['file_link'])
        new_entry.save()
        return Response(status=status.HTTP_201_CREATED)

# def getSchedule(self):
#     schedule = list()
#     df = pd.read_csv("https://docs.google.com/spreadsheets/d/1NZP84iehcwRFmXVLQR2tMzcpz4qUhado/export?format=csv&gid=387283422", index_col=0) #stores the CSV file into a data frame
#     #note when uploading new csvfile, change to /export?format=csv
#     name_formatted = ", ".join(self._name.split(" ")[::-1])                                                                                   #reformats name into last, first
#     rowAccessed = df.loc[name_formatted]                                                                                                      #locates the row cooresponding to the name
#     rowAccessed.dropna(how = "all", inplace=True)                                                                                             #removes all NaN columns
#     rowAccessed.drop(rowAccessed[rowAccessed == "A"].index, inplace = True)                                                                   #removes all A columns
#     return list(rowAccessed[:-2].index)
