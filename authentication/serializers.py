import re
from rest_framework import serializers
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