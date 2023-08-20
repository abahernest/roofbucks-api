from django.urls import path
from .views import (KycVerificationApiView)

urlpatterns = [
    path('kyc-verification/', KycVerificationApiView.as_view(), name='kyc_verification'),
]
