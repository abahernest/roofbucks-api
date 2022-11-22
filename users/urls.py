from django.urls import path
from .views import (Profile, CreateCompany, AddBankInformation)

urlpatterns = [
    path('profile/', Profile.as_view(), name='profile'),
    path('add_business/', CreateCompany.as_view(), name='add_business'),
    path('add_bank_information/', AddBankInformation.as_view(),
         name='add_bank_information'),
]
