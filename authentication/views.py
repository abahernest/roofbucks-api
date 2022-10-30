from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from users.models import User
from .serializers import SignupSerializer

class SignupView(generics.GenericAPIView):

    serializer_class = SignupSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.validated_data

        # check that user doesn't exist
        users = User.objects.filter(phone=user_data['email'])
        if len(users) > 0 :
            return Response({
                "message": "User already exists",
            }, 400)

        # pesist user in db
        user = serializer.save()

        # generate jwt
        user_data["token"] = str(RefreshToken.for_user(user).access_token)

        return Response(user_data, status=status.HTTP_201_CREATED)

