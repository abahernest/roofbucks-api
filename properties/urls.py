from django.urls import path
from .views import (NewPropertyAPIView)

urlpatterns = [
    path('new/', NewPropertyAPIView.as_view(), name='new_property'),
]
