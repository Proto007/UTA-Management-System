from rest_framework import serializers
from .models import DataIO

class DataIOSerializer(serializers.ModelSerializer):
    """
    Serializer for DataIO model
    """
    class Meta:
        model = DataIO
        fields = ('file_link',)
        lookup_field = 'file_link'

