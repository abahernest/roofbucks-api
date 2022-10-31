from datetime import timedelta
from django.utils import timezone
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from users.models import User
from .models import EmailVerification
from .serializers import EmailVerificationSerializer, SignupSerializer, LoginSerializer
from utils.email import SendMail

class SignupView(generics.GenericAPIView):

    serializer_class = SignupSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # check that user doesn't exist
        users = User.objects.filter(phone=serializer.validated_data['email'])
        if len(users) > 0 :
            return Response({
                "message": "User already exists",
            }, status.HTTP_400_BAD_REQUEST)

        # pesist user in db
        user = serializer.save()
        
        user_data = serializer.data

        # generate email verification token
        token = User.objects.make_random_password(length=6, allowed_chars='0123456789')
        token_expiry = timezone.now() + timedelta(minutes=6)

        EmailVerification.objects.create(user=user, token=token, token_expiry=token_expiry)

        # Send Mail
        data = {"token":token, "firstname": user.firstname, 'to_email': user.email}
        SendMail.send_email_verification_mail(data)

        return Response(user_data, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyEmail(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "successful"}, status=status.HTTP_200_OK)
