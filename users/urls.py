from django.urls import path
from .views import (UpdateProfile, profile)

urlpatterns = [
    path('profile/', profile, name='profile'),
    path('update-profile/', UpdateProfile.as_view(), name='update-profile')
]
