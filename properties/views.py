from rest_framework import (views, permissions, parsers)
from rest_framework.response import Response
from django.db import transaction

from .serializers import NewPropertySerializer
from authentication.permissions import IsAgent

class NewPropertyAPIView(views.APIView):

    serializer_class = NewPropertySerializer
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]
    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def post(self, request):
        
        serializer = self.serializer_class(data= request.data)
        serializer.is_valid(raise_exception=True)

        serializer.validated_data['agent'] = request.user

        with transaction.atomic():
            serializer.save()
    
        return Response( {'message':'successful'}, status=200)