from rest_framework import serializers
from .models import *

class DataIOSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataIO
        fields = ('file_link',)
        lookup_field = 'file_link'

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ('description', 'day', 'start', 'end')
        lookup_field = 'description'

class UTASerializer(serializers.ModelSerializer):
    class Meta:
        model = UTA
        fields = ('lastname', 'firstname', 'emplid', 'shifts' )
        lookup_field = 'emplid'

class RandomPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = RandomPass
        fields = ['random_pass']
        read_only_fields = ['random_pass']

class CheckinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkin
        fields = ['emplid', 'shift', 'late_mins', 'number_of_shifts']
        read_only_fields = ['shift', 'late_mins']
