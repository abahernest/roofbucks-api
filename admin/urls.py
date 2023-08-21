from django.urls import path
from .views import (KycVerificationApiView, PropertyModerationApiView,
                    ReviewPropertyOwnershipRequest, PropertyOwnershipRequestsViewset)

urlpatterns = [
    path('kyc_verification/', KycVerificationApiView.as_view(), name='kyc_verification'),
    path('moderate_property/', PropertyModerationApiView.as_view(), name='moderate_property'),
    path('review_property_ownership/', ReviewPropertyOwnershipRequest.as_view(), name='review_property_ownership_request'),
    path(
        'property_ownership_requests/', PropertyOwnershipRequestsViewset.as_view({'get': 'list'}), name='property_ownership_requests'),
]
