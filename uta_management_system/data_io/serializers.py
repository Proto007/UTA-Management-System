from rest_framework import serializers

from .models import *


class DataIOSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataIO
        fields = ("file_link",)
        lookup_field = "file_link"


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ("description", "day", "start", "end")
        lookup_field = "description"


class UTASerializer(serializers.ModelSerializer):
    class Meta:
        model = UTA
        fields = ("fullname", "emplid", "shifts")
        lookup_field = "emplid"


class RandomPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = RandomPass
        fields = ["random_pass"]
        read_only_fields = ["random_pass"]


class CheckinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkin
        fields = [
            "created_at",
            "emplid",
            "shift",
            "late_mins",
            "number_of_shifts",
            "covered_by",
            "alternate_day",
        ]
        read_only_fields = ["created_at", "shift", "late_mins"]


class TimeSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSheet
        fields = ["start_date", "end_date"]
