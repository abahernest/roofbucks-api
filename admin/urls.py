from django.urls import path
from .views import (KycVerificationApiView, PropertyModerationApiView, ReviewPropertyOwnershipRequest)

urlpatterns = [
    path('kyc_verification/', KycVerificationApiView.as_view(), name='kyc_verification'),
    path('moderate_property/', PropertyModerationApiView.as_view(), name='moderate_property'),
    path('review_property_ownership/', ReviewPropertyOwnershipRequest.as_view(), name='review_property_ownership_request'),
]
