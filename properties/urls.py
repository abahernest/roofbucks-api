from django.urls import path
from .views import (NewPropertyAPIView, StayPeriodAPIView, PropertyListView, PropertyDetailView, UpdatePropertyAPIView)

urlpatterns = [
    path(
        '', PropertyListView.as_view({'get': 'list'}), name='all_properties'),
    path('new/', NewPropertyAPIView.as_view(), name='new_property'),
    path('stay-periods/<property_id>/',
         StayPeriodAPIView.as_view(), name='add_stay_periods'),
    path('stay-periods/<property_id>/<index_of_stay_period>/',
         StayPeriodAPIView.as_view(), name='delete_stay_periods'),
    path('single/<property_id>/', PropertyDetailView.as_view(), name='single_property'),
    path('update/<property_id>/', UpdatePropertyAPIView.as_view(), name='update_property'),
]
