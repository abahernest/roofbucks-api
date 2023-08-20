from rest_framework import (views, permissions)
from rest_framework.response import Response
from .serializers import (
    KycVerificationSerializer,)
from users.models import User

class KycVerificationApiView(views.APIView):

    serializer_class = KycVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': request.data['kyc_verification_status']}, status=200)

