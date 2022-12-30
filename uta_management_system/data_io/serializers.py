from rest_framework import serializers
from .models import *

class DataIOSerializer(serializers.ModelSerializer):
    """
    Serializer for DataIO model
    """
    class Meta:
        model = DataIO
        fields = ('file_link',)
        lookup_field = 'file_link'

class ShiftSerializer(serializers.ModelSerializer):
    """
    Serializer for Shift model
    """
    class Meta:
        model = Shift
        fields = ('description', 'day', 'start', 'end')
        lookup_field = 'description'

class UTASerializer(serializers.ModelSerializer):
    """
    Serializer for UTA model
    """
    class Meta:
        model = UTA
        fields = ('lastname', 'firstname', 'emplid', 'shifts' )
        lookup_field = 'emplid'
