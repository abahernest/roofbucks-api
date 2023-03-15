from django.urls import path
from .views import (Profile, CreateCompany, AccountSettingsView,
                    AddBankInformation, BusinessProfileView, 
                    AgentListView, ReviewCreateView, ReviewListView)

urlpatterns = [
    path('agent_list/', AgentListView.as_view({'get':'list'}), name='agent_list'),
    path('profile/', Profile.as_view(), name='profile'),
    path('add_business/', CreateCompany.as_view(), name='add_business'),
    path('add_bank_information/', AddBankInformation.as_view(),
         name='add_bank_information'),
    path('business_profile/<user_id>/',
         BusinessProfileView.as_view(), name='business_profile'),
    path('business_reviews/<company_id>/', ReviewListView.as_view(),
         name='list-reviews'),
    path('add_reviews/<company_id>/', ReviewCreateView.as_view(),
         name='create-reviews'),
    path('account_settings/', AccountSettingsView.as_view(),
         name='account_settings')
]
