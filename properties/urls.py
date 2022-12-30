from django.urls import path
from .views import (NewPropertyAPIView, StayPeriodAPIView)

urlpatterns = [
    path('new/', NewPropertyAPIView.as_view(), name='new_property'),
    path('stay-periods/<property_id>/',
         StayPeriodAPIView.as_view(), name='add_stay_periods'),
    path('stay-periods/<property_id>/<index_of_stay_period>/',
         StayPeriodAPIView.as_view(), name='delete_stay_periods'),
]
