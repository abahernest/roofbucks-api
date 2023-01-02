from django.urls import path
from .views import (NewPropertyAPIView, StayPeriodAPIView,
                    PropertyListView, RemoveMediaView)

urlpatterns = [
    path(
        '', PropertyListView.as_view({'get': 'list'}), name='all_properties'),
    path('new/', NewPropertyAPIView.as_view(), name='new_property'),
    path('stay-periods/<property_id>/',
         StayPeriodAPIView.as_view(), name='add_stay_periods'),
    path('stay-periods/<property_id>/<index_of_stay_period>/',
         StayPeriodAPIView.as_view(), name='delete_stay_periods'),
    path('media/<media_type>/<property_id>/<media_id>/', RemoveMediaView.as_view(), name='property_media'),
]
