from django.shortcuts import render
from .models import DataIO
from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.permissions import  IsAdminUser
from .serializers import DataIOSerializer

# Create your views here.
class DataIOViewSet(viewsets.ModelViewSet):
    """
    Viewset to modify the schedule link and return timesheet
    """
    permission_classes = (IsAdminUser,)
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
