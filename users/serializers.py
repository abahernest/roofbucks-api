from rest_framework import serializers
from django.utils import timezone, dateparse

dateparse.parse_date

from .models import User, Company, Review
from album.models import MediaAlbum, MediaFiles
from utils.constants import ALLOWABLE_DOCUMENT_TYPES
from properties.serializers import PropertySerializer


class UpdateProfileSerializer(serializers.ModelSerializer):

    def validate_file_extension(value):
        if value.content_type not in ALLOWABLE_DOCUMENT_TYPES:
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

    email = serializers.EmailField(min_length=3, read_only=True)
    display_photo = serializers.ImageField(
        max_length=256, allow_empty_file=False, required=False)
    proof_of_address_document = serializers.FileField(
        max_length=256, allow_empty_file=False, validators=[validate_file_extension, validate_file_size])
    identity_documents = serializers.ListField(
        child=serializers.FileField(
            allow_empty_file=False,
            max_length=256,
            validators=[validate_file_extension, validate_file_size]
        ),
        # write_only=True,
        required=False,
        min_length=2,
        max_length=2
    )
    identity_document_type = serializers.ChoiceField(IDENTITY_DOCUMENT_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'date_of_birth', 'email', 'address',
                  'city', 'country', 'phone', 'identity_document_type',
                  'identity_document_number', 'identity_document_expiry_date',
                  'display_photo', 'proof_of_address_document', 'identity_documents'
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

    def update(self, instance: User, validated_data):

        ## add identity documents to album
        media_files_array, updatable_fields = [], {}

        for key in validated_data:
            if key == 'identity_documents':
                if not instance.identity_document_album:

                    identity_documents = validated_data.get('identity_documents')

                    album = MediaAlbum.objects.create()
                    for document in identity_documents:
                        media_files_array.append(
                            MediaFiles(album=album, document=document, media_type='DOCUMENT'))

                    MediaFiles.objects.bulk_create(media_files_array)
                    updatable_fields['identity_document_album'] = album
            else:
                updatable_fields[key] = validated_data.get(key)

        instance.stages_of_profile_completion["profile"] = True
        instance.save()
        User.objects.filter(id=instance.id).update(**updatable_fields)

        return instance



class CreateCompanySerializer(serializers.ModelSerializer):

    def validate_file_extension(value):
        if value.content_type not in ALLOWABLE_DOCUMENT_TYPES:
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
        max_length=256, allow_empty_file=False, validators=[validate_file_extension, validate_file_size],
        required=False)
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
                  'city', 'country', 'display_name', 'website', 'description', ]

    def validate(self, attrs):
        phone = attrs.get('phone', '')
        email = attrs.get('email', '')

        if not str(phone).isdigit():
            raise serializers.ValidationError("phone must contain only digits")

        company_objects = Company.objects.filter(phone=phone)
        if len(company_objects) > 0:
            raise serializers.ValidationError("phone already taken")

        company_objects = Company.objects.filter(email=email)
        if len(company_objects) > 0:
            raise serializers.ValidationError("email already taken")

        return attrs


class AddBankInfoSerializer(serializers.ModelSerializer):
    bank_information = serializers.DictField(child=serializers.CharField(min_length=3))

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

    def update(self, instance, validated_data):
        bank_info = validated_data.get('bank_information')

        instance.bank_information.append(bank_info)
        user = instance.user
        user.stages_of_profile_completion['billing'] = True
        user.save()
        instance.save()

        return instance.bank_information


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class ReviewersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'display_photo', 'firstname', 'lastname']


class ReviewsSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(max_value=5, min_value=1, required=False)
    review = serializers.CharField(required=False)
    reviewer = ReviewersSerializer(required=False)

    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Review
        fields = ['rating', 'review', 'reviewer', 'created_at']

    def validate(self, attrs):
        rating = attrs.get('rating')
        review = attrs.get('review')

        if not rating and not review:
            raise serializers.ValidationError(
                "must provide 'review' or 'rating'.")

        return attrs

    def create(self, validated_data) -> Review:
        return Review.objects.create(
            **validated_data
        )


class BusinessProfileSerializer(serializers.ModelSerializer):
    company = CompanySerializer(required=False)
    properties = PropertySerializer(many=True, required=False)
    reviews = ReviewsSerializer(many=True, required=False)
    rating = serializers.DecimalField(required=False, decimal_places=1, max_digits=2, read_only=True)

    class Meta:
        model = User
        exclude = ['password']


class AgentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'firstname', 'lastname', 'phone',
                  'email', 'city', 'country', 'secondary_phone',
                  'display_photo', 'title', 'summary']
