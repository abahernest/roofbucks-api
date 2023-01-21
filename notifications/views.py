from rest_framework import (views, permissions)
from rest_framework.response import Response

from .serializers import NotificationsSerializer
from .models import Notifications

class NotificationsListView(views.APIView):

    serializer_class = NotificationsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        notifications = Notifications.objects.filter(
            user=request.user).order_by("-created_at")

        serializer = self.serializer_class(notifications, many=True)

        return Response(serializer.data, status=200)


