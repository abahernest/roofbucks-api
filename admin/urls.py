from django.urls import path
from .views import (KycVerificationApiView)

urlpatterns = [
    path('kyc_verification/', KycVerificationApiView.as_view(), name='kyc_verification'),
]
