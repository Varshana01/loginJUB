from rest_framework import serializers
from .models import Users

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['username', 'email', 'password']
