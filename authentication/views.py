import os
from datetime import timedelta
from django.utils import timezone
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes, smart_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.http import HttpResponsePermanentRedirect, HttpResponse
from django.db import transaction

from users.models import User
from .models import EmailVerification
from .serializers import (
    EmailVerificationSerializer,
    RequestPasswordResetEmailSerializer, 
    SignupSerializer, 
    LoginSerializer, 
    RequestPasswordResetEmailSerializer,
    SetNewPasswordSerializer
    )
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

        with transaction.atomic():
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

        return Response({"message": "Registration successful. Check email for verification code"}, status=status.HTTP_201_CREATED)

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


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = RequestPasswordResetEmailSerializer

    def post(self, request):
        
        # validate request body
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # serializer validated_data retuns custom "False" value if encounters error
        if serializer.validated_data != False:
            #send mail
            SendMail.send_password_reset_mail(serializer.data, request=request)

        return Response({'message': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class CustomRedirect(HttpResponsePermanentRedirect):

    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']

class PasswordTokenCheckAPI(generics.GenericAPIView):

    def get(self, request, uid64, token):
        try:
            redirect_url = os.environ.get('PASSWORD_RESET_REDIRECT_URL', '')
            user_id = smart_str(urlsafe_base64_decode(uid64))
            user = User.objects.get(id=user_id)
            
            if not PasswordResetTokenGenerator().check_token(user, token):
                return HttpResponse('<p>Invalid Token. Request a new one</p>', status=400)

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(redirect_url+f'&token_valid=True&uid64={uid64}&token={token}')
            return HttpResponse('<p>Contact Admin. Page Not found</p>', status=400)
        except Exception as e:
            return HttpResponse('<p>Invalid Token. Request a new one</p>', status=400)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
