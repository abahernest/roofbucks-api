from django.urls import path
from .views import (NotificationsListView)

urlpatterns = [
    path('', NotificationsListView.as_view(),name='user_notifications'),
]
