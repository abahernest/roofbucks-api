from rest_framework import serializers
from django.utils import timezone, dateparse
dateparse.parse_date

from .models import User, Company
from properties.serializers import PropertySerializer

class UpdateProfileSerializer (serializers.ModelSerializer):

    def validate_file_extension(value):
        if value.content_type not in ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']:
            raise serializers.ValidationError('Only PDF, JPG, JPEG, PNG files are allowed')

    def validate_file_size(value):
        max_size = 8388608
        if value.size > max_size:
            raise serializers.ValidationError('Maximum file size is 8MB')


    IDENTITY_DOCUMENT_CHOICES = [
        ("NATIONAL_ID", "National ID Card"),
        ("DRIVERS_LICENSE", "Drivers License"),
        ("PASSPORT", "Passport")
    ]

    email = serializers.EmailField(min_length=3,read_only=True)
    display_photo = serializers.ImageField(
        max_length=256, allow_empty_file=False, required = False)
    proof_of_address_document = serializers.FileField(
        max_length=256, allow_empty_file=False, validators=[validate_file_extension, validate_file_size])
    identity_document_front = serializers.FileField(
        max_length=256, allow_empty_file=False, validators=[validate_file_extension, validate_file_size])
    identity_document_back = serializers.FileField(
        max_length=256, allow_empty_file=False, validators=[validate_file_extension, validate_file_size])
    identity_document_type = serializers.ChoiceField(IDENTITY_DOCUMENT_CHOICES, required=True)
    date_of_birth       = serializers.DateField()
    phone               = serializers.CharField(min_length=4)
    firstname           = serializers.CharField(min_length=2, max_length=65)
    lastname            = serializers.CharField(min_length=2, max_length=65)
    city                = serializers.CharField(min_length=2, max_length=255, required=False)
    address             = serializers.CharField(min_length=2)
    country             = serializers.CharField(min_length=2, max_length=65)
    identity_document_expiry_date = serializers.DateField()
    identity_document_number      = serializers.CharField(min_length=2, max_length=255)


    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'date_of_birth', 'email', 'address',
                  'city', 'country', 'phone', 'identity_document_type', 'identity_document_front', 'identity_document_back',
                  'identity_document_number', 'identity_document_expiry_date', 
                  'display_photo', 'proof_of_address_document',
                  ]

    def validate(self, attrs):
        phone = attrs.get('phone', '')
        date_of_birth = str(attrs.get('date_of_birth', ''))
        identity_document_expiry_date = str(attrs.get(
            'identity_document_expiry_date', ''))

        if not str(phone).isdigit():
            raise serializers.ValidationError("phone must contain only digits")

        valid_date = dateparse.parse_date(date_of_birth)
        if not valid_date:
            raise serializers.ValidationError("date_of_birth must contain valid date string")

        if valid_date > timezone.now().date():
            raise serializers.ValidationError('date_of_birth cannot be a future date')

        valid_date = dateparse.parse_date(identity_document_expiry_date)
        if not valid_date:
            raise serializers.ValidationError(
                "identity_document_expiry_date must contain valid date string")

        if valid_date <= timezone.now().date():
            raise serializers.ValidationError(
                'identity_document_expiry_date should be a future date')
        
        return attrs


class CreateCompanySerializer (serializers.ModelSerializer):

    def validate_file_extension(value):
        if value.content_type not in ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']:
            raise serializers.ValidationError(
                'Only PDF, JPG, JPEG, PNG files are allowed')

    def validate_file_size(value):
        max_size = 8388608
        if value.size > max_size:
            raise serializers.ValidationError('Maximum file size is 8MB')


    email = serializers.EmailField(min_length=3)
    company_logo = serializers.ImageField(
        max_length=256, allow_empty_file=False, required=False)
    certificate_of_incorporation = serializers.FileField(
        max_length=256, allow_empty_file=False, validators=[validate_file_extension, validate_file_size] ,required=False)
    reference_number = serializers.CharField(min_length=4)
    phone = serializers.CharField(min_length=4)
    display_name = serializers.CharField(min_length=2, max_length=65)
    website = serializers.CharField(min_length=2, required=False)
    city = serializers.CharField(min_length=2, max_length=255)
    country = serializers.CharField(min_length=2, max_length=65)
    description = serializers.CharField(required=False)

    class Meta:
        model = Company
        fields = ['email', 'company_logo', 'certificate_of_incorporation', 'reference_number', 'phone',
                  'city', 'country', 'display_name', 'website', 'description',]

    def validate(self, attrs):
        phone = attrs.get('phone', '')
        email = attrs.get('email', '')

        if not str(phone).isdigit():
            raise serializers.ValidationError("phone must contain only digits")

        company_objects = Company.objects.filter(phone=phone)
        if len(company_objects) >0:
            raise serializers.ValidationError("phone already taken")

        company_objects = Company.objects.filter(email=email)
        if len(company_objects) > 0:
            raise serializers.ValidationError("email already taken")

        return attrs


class AddBankInfoSerializer (serializers.ModelSerializer):

    bank_information = serializers.DictField(child = serializers.CharField(min_length=3))

    class Meta:
        model = Company
        fields = ["bank_information"]

    def validate(self, attrs):
        bank_information = attrs.get("bank_information")

        keys = sorted(bank_information.keys())
        expected_keys = ['account_name', 'account_number', 'bank_name', 'country']
        if keys != expected_keys:
            raise serializers.ValidationError(
                "Bank Information should be a map of 'account_name', 'account_number', 'bank_name', 'country' ")

        if not bank_information.get("account_number", '').isdigit():
            raise serializers.ValidationError("Account number must be a string of numbers")
        
        return attrs


    def update (self, instance, validated_data):
        bank_info = validated_data.get('bank_information')

        instance.bank_information.append(bank_info)
        instance.save()

        return instance.bank_information

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class CompanySerializer (serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'


class BusinessProfileSerializer (serializers.ModelSerializer):

    company = CompanySerializer(required=False)
    properties = PropertySerializer(many=True, required=False)

    class Meta:
        model = User
        exclude = ['password']
