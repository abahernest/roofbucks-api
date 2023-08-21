from rest_framework import (views, permissions)
from rest_framework.response import Response
from .serializers import (
    KycVerificationSerializer, PropertyModerationSerializer,
    ReviewPropertyOwnershipSerializer)

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
