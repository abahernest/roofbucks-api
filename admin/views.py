from rest_framework import (views, permissions)
from rest_framework.response import Response
from .serializers import (
    KycVerificationSerializer, PropertyModerationSerializer,
    ReviewPropertyOwnershipSerializer)
from properties.serializers import  PropertyOwnershipSerializer, PropertyOwnership, \
    CHOICES_FOR_PROPERTY_OWNERSHIP_STATUS, CHOICES_FOR_PROPERTY_OWNER_TYPE
from rest_framework.viewsets import ReadOnlyModelViewSet
from utils.pagination import CustomPagination


class KycVerificationApiView(views.APIView):

    serializer_class = KycVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': request.data['kyc_verification_status']}, status=200)

class PropertyModerationApiView(views.APIView):

    serializer_class = PropertyModerationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': request.data['status']}, status=200)

class ReviewPropertyOwnershipRequest(views.APIView):
    serializer_class = ReviewPropertyOwnershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({"message": request.data['status']}, status=200)


class PropertyOwnershipRequestsViewset(ReadOnlyModelViewSet):

    serializer_class = PropertyOwnershipSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = PropertyOwnership.objects.filter()

        status = self.request.query_params.get('status')
        if status is not None:
            queryset = queryset.filter(status__iexact=status)

        user_type = self.request.query_params.get('user_type')
        if user_type is not None:
            queryset = queryset.filter(user_type__iexact=user_type)

        queryset = queryset.order_by('-created_at')
        return queryset