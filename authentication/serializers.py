from django.utils import timezone
import re
from rest_framework import serializers
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed, ParseError

from users.models import User
from .models import EmailVerification

class SignupSerializer (serializers.ModelSerializer):
    password    = serializers.CharField(min_length=8, max_length=68,write_only=True)

    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'password', 'email']


    def validate (self, attrs):
        firstname = attrs.get('firstname', '')
        lastname = attrs.get('lastname', '')
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        if not firstname.isalpha():
            raise serializers.ValidationError("Fistname must contain alphabets only")


        if not lastname.isalpha():
            raise serializers.ValidationError("Lastname must contain alphabets only")


        if re.search('[A-Z]',password) is None:
            raise serializers.ValidationError("Password must contain One Uppercase Alphabet")

        if re.search('[a-z]', password) is None:
            raise serializers.ValidationError("Password must contain One Lowercase Alphabet")

        if re.search('[0-9]', password) is None:
            raise serializers.ValidationError("Password must contain One Numeric Character")

        if re.search(r"[@$!%*#?&]", password) is None:
            raise serializers.ValidationError("Password must contain One Special Character")

        return attrs


    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=6, min_length=6, write_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = User
        fields = ['token', 'email']

    def validate(self,attrs):
        email = attrs.get('email', '')
        token = attrs.get('token', '')

        users = User.objects.filter(email=email)
        if len(users) <= 0:
            raise ParseError('User not found')
        
        user = users[0]
        verificationObj = EmailVerification.objects.filter(user=user)

        if len(verificationObj) <= 0:
            raise ParseError('User not found')
            
        verificationObj = verificationObj[0]
        if verificationObj.token != token:
            raise ParseError('Wrong Token')

        if verificationObj.is_verified:
            raise ParseError('Token Expired')

        if verificationObj.token_expiry < timezone.now():
            raise ParseError('Token Expired')

        verificationObj.is_verified=True
        verificationObj.token_expiry=timezone.now()
        verificationObj.save()
        user.is_verified=True
        user.save()

        return True
            

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=8, write_only=True)
    firstname = serializers.CharField(
        max_length=255, min_length=3, read_only=True)
    lastname = serializers.CharField(
        max_length=255, min_length=3, read_only=True)
    role = serializers.CharField(
        max_length=255, min_length=3, read_only=True)


    class Meta:
        model = User
        fields = ['email', 'password', 'tokens', 'firstname', 'lastname', 'role']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Please verify your email')

        return {
            'email': user.email,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'role': user.role,
            'tokens': user.tokens
        }
