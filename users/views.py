from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import views
from .serializers import (UpdateProfileSerializer)
from rest_framework import (parsers,permissions,authentication)

from .models import User

def profile(request):
    return JsonResponse("Profile Endpoint", safe=False)


class UpdateProfile(views.APIView):

    serializer_class = UpdateProfileSerializer
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]

    def patch(self,request):

        user_id = request.user.id
        user = User.objects.get(id=user_id)

        serializer = self.serializer_class(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        serializer.save()

        return Response(serializer.data, status=200)
        