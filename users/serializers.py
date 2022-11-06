from rest_framework import serializers
from django.utils import timezone, dateparse
dateparse.parse_date
from .models import User


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
        max_length=256, allow_empty_file=False)
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
