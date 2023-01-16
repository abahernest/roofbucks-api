from rest_framework import serializers

from .models import Notifications


class NotificationsSerializer (serializers.ModelSerializer):

    class Meta:
        model = Notifications
        fields = ["status", "message", "created_at"]

