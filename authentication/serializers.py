import re
from rest_framework import serializers
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed

from users.models import User

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



class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=8, write_only=True)
    firstname = serializers.CharField(
        max_length=255, min_length=3, read_only=True)
    lastname = serializers.CharField(
        max_length=255, min_length=3, read_only=True)


    class Meta:
        model = User
        fields = ['email', 'password', 'tokens', 'firstname', 'lastname']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')

        return {
            'email': user.email,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'tokens': user.tokens
        }
