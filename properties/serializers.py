import json
from rest_framework import serializers
from rest_framework.exceptions import ParseError


from .models import Property, ShoppingCart, PropertyInspection, CHOICES_FOR_INSPECTION_STATUS
from album.models import MediaFiles, MediaAlbum
from album.serializers import MediaAlbumSerializer, MediaFilesSerializer
from utils.constants import (
    ALLOWABLE_NUMBER_OF_DOCUMENTS, ALLOWABLE_NUMBER_OF_IMAGES, ALLOWABLE_DOCUMENT_TYPES)
from utils.date import (greater_than_today)



class NewPropertySerializer (serializers.ModelSerializer):

    def validate_file_extension(value):
        if value.content_type not in ALLOWABLE_DOCUMENT_TYPES:
            raise serializers.ValidationError(
                'Only PDF, JPG, JPEG, PNG files are allowed')

    def validate_file_size(value):
        max_size = 8388608
        if value.size > max_size:
            raise serializers.ValidationError('Maximum file size is 8MB')

    default_image = serializers.ImageField(
        allow_empty_file=False,
        max_length=256,
        validators=[validate_file_size],
        required=False,
    )

    images = serializers.ListField(
        child= serializers.ImageField(
            allow_empty_file=False,
            max_length = 256,
            validators=[validate_file_size]
            ),
        write_only= True,
        required=False,
        min_length=1,
        max_length=ALLOWABLE_NUMBER_OF_IMAGES
    )
    approved_survey_plan = serializers.FileField(
            allow_empty_file=False,
            max_length = 256,
            required=False,
            validators=[validate_file_extension, validate_file_size]
            )
    purchase_receipt = serializers.FileField(
            allow_empty_file=False,
            max_length = 256,
            required=False,
            validators=[validate_file_extension, validate_file_size]
            )
    excision_document = serializers.FileField(
            allow_empty_file=False,
            max_length = 256,
            required=False,
            validators=[validate_file_extension, validate_file_size]
            )
    gazette_document = serializers.FileField(
            allow_empty_file=False,
            max_length = 256,
            required=False,
            validators=[validate_file_extension, validate_file_size]
            )
    certificate_of_occupancy = serializers.FileField(
            allow_empty_file=False,
            max_length = 256,
            required=False,
            validators=[validate_file_extension, validate_file_size]
            )
    registered_deed_of_assignment = serializers.FileField(
            allow_empty_file=False,
            max_length = 256,
            required=False,
            validators=[validate_file_extension, validate_file_size]
            )
    scheduled_stays = serializers.CharField(required=False)

    class Meta:
        model = Property
        # fields = '__all__'
        fields = ['id','name', 'description', 'completion_status', 'apartment_type', 'address', 'city', 
        'state','country', 'percentage_discount', 'promotion_closing_date', 'promotion_type', 'other_deals',
        'number_of_bedrooms', 'number_of_toilets', 'benefits', 'amenities', 'ERF_size', 'dining_area', 'cross_streets',
        'landmarks', 'floor_size', 'date_built', 'price_per_share', 'completion_cost', 'completion_date', 'zip_code',
        'percentage_completed', 'total_number_of_shares', 'total_property_cost', 'expected_ROI', 'area_rent_rolls',
        'scheduled_stays', 'images', 'company', 'company_name', 'image_album', 'document_album',
        'registered_deed_of_assignment', 'certificate_of_occupancy', 'gazette_document', 'excision_document', 'purchase_receipt',
        'approved_survey_plan', 'default_image'
        ]
        read_only_fields=['id','company','company_name', 'image_album', 'document_album' ]

    def validate(self, attrs):
        benefits = attrs.get('benefits','')
        amenities = attrs.get('amenities')
        cross_streets = attrs.get('cross_streets')
        landmarks = attrs.get('landmarks')
        scheduled_stays = attrs.get('scheduled_stays')

        ## using form inputs parses the string in an array
        if benefits:
            attrs['benefits'] = benefits[0].strip().split(',')

        if amenities:
            attrs['amenities'] = amenities[0].strip().split(',')

        if cross_streets:
            attrs['cross_streets'] = cross_streets[0].strip().split(',')

        if landmarks:
            attrs['landmarks'] = landmarks[0].strip().split(',')

        if scheduled_stays:
            final_scheduled_stays = []

            ## use ',,' to seperate stay periods and ',' to seperate start and end date
            scheduled_stays = scheduled_stays.strip().split(',,')

            for stay_period in scheduled_stays:
                final_scheduled_stays.append(stay_period.split(','))

            attrs['scheduled_stays'] = json.dumps(final_scheduled_stays)

        return attrs
            
    def create(self, validated_data):
        media_files_array = []

        uploaded_images = validated_data.get('images')
        uploaded_documents = validated_data.get('documents')
        default_image = validated_data.get('default_image')

        
        image_album, document_album = None, None

        if uploaded_images:

            ## if 'images' is part of request payload, then 'default_image' must be passed also
            if not default_image:
                raise serializers.ValidationError({"default_image":"default_image field is required"})


            validated_data.pop('images')
            image_album = MediaAlbum.objects.create()
            
            for image in uploaded_images:
                media_files_array.append(
                    MediaFiles(album=image_album, image=image, media_type='IMAGE') )


        if uploaded_documents:
            validated_data.pop('documents')
            document_album = MediaAlbum.objects.create()

            for document in uploaded_documents:
                media_files_array.append(
                    MediaFiles(album=document_album, document=document, media_type='DOCUMENT') )

        if len(media_files_array)>0:
            MediaFiles.objects.bulk_create(media_files_array)

        scheduled_stays = validated_data.get('scheduled_stays')
        if scheduled_stays:
            validated_data['scheduled_stays'] = json.loads(scheduled_stays)
        
        property = Property.objects.create(
            **validated_data,
            image_album=image_album,
            document_album=document_album)

        return property

    def update(self, instance, validated_data):

        # count existing images and documents for this property if user is attempting to update image/document
        total_images_uploaded, total_documents_uploaded = None, None

        if validated_data.get('images'):
            images = instance.get_images()
            total_images_uploaded = len(images)
        if validated_data.get('documents'): 
            documents = instance.get_documents()
            total_documents_uploaded = len(documents)

        updatable_fields = {}
        for key in validated_data:
            if key in ['agent', 'image_album', 'document_album', 'moderation_status']:
                raise ParseError('Attempting to change Fixed Values')

            if key == 'images':

                ## if 'images' is part of request payload, then 'default_image' must be passed also
                ## as long as property doesn't already have default image
                if (not instance.default_image) and (not validated_data.get('default_image')):
                    raise serializers.ValidationError({"default_image":["default_image field is required"]})

                media_files_array = []
                image_album = instance.image_album

                # fetch count of remaining allowable number of images
                remaining_number_of_images = ALLOWABLE_NUMBER_OF_IMAGES - total_images_uploaded
                # remaining_number_of_documents= ALLOWABLE_NUMBER_OF_DOCUMENTS - total_document_uploaded

                # ensure image uploaded doesn't exceed allowable number
                uploaded_images = validated_data.get('images')
                if total_images_uploaded > ALLOWABLE_NUMBER_OF_IMAGES:
                    raise ParseError('Exceeded alloted number of images. Delete existing images for this Property')
                    
                elif total_images_uploaded == 0:
                    image_album = MediaAlbum.objects.create()

                elif remaining_number_of_images < len(uploaded_images):
                    raise ParseError(
                        f'Only {remaining_number_of_images} slots left for images. Delete existing images for this Property to obtain more slots')

                for image in uploaded_images:
                    media_files_array.append(
                        MediaFiles(album=image_album, image=image, media_type='IMAGE'))

                MediaFiles.objects.bulk_create(media_files_array)
                updatable_fields['image_album'] = image_album

                # select one image as default_image if none
                if not instance.default_image:
                    updatable_fields['default_image'] = uploaded_images[0]

            elif key == 'documents':
                media_files_array = []
                document_album = instance.document_album

                # fetch count of remaining allowable number of images
                remaining_number_of_documents = ALLOWABLE_NUMBER_OF_DOCUMENTS - total_documents_uploaded

                # ensure image uploaded doesn't exceed allowable number
                uploaded_documents = validated_data.get('documents')
                if total_documents_uploaded > ALLOWABLE_NUMBER_OF_DOCUMENTS:
                    raise ParseError('Exceeded alloted number of documents. Delete existing documents for this Property')
                elif total_documents_uploaded == 0:
                    document_album = MediaAlbum.objects.create()
                elif remaining_number_of_documents < len(uploaded_documents):
                    raise ParseError(
                        f'Only {remaining_number_of_documents} slots left for documents. Delete existing documents for this Property to obtain more slots')

                for document in uploaded_documents:
                    media_files_array.append(
                        MediaFiles(album=document_album, document=document, media_type='DOCUMENT'))

                MediaFiles.objects.bulk_create(media_files_array)
                updatable_fields['document_album'] = document_album

            elif key == 'scheduled_stays':
                updatable_fields[key] = instance.scheduled_stays + json.loads(validated_data.get(key))
            else:
                updatable_fields[key] = validated_data.get(key)

        return Property.objects.filter(id=instance.id).update(**updatable_fields)

class StayPeriodSerializer (serializers.Serializer):

    stay_periods = serializers.ListField(
        child=serializers.ListField(
            child= serializers.DateField()
        ),
        write_only=True,
        min_length=1
    )

    def update(self, instance, validated_data):
        
        scheduled_stays = validated_data.get('stay_periods')

        instance.scheduled_stays+=scheduled_stays
        instance.save()

        return instance


class PropertySerializer (serializers.ModelSerializer):

    images = MediaFilesSerializer(many=True, required=False)
    documents = MediaFilesSerializer(many=True, required=False)    
    class Meta:
        model = Property
        fields = '__all__'


class SimilarPropertyListSerializer (serializers.ModelSerializer):

    images = MediaFilesSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = ['id', 'name', 'company_name', 'address', 'city',
                  'state', 'country', 'number_of_bedrooms', 'images',
                  'number_of_toilets', 'percentage_discount', 'total_property_cost']

class PropertyTableSerializer (serializers.ModelSerializer):

    class Meta:
        model = Property
        fields = ['id', 'name', 'created_at',
                  'moderation_status', 'total_property_cost']

class PropertyListingSerializer (serializers.ModelSerializer):

    class Meta:
        model = Property
        fields = ['id', 'name', 'created_at', 'company_name', 'agent',
                  'apartment_type', 'address', 'city', 'state', 'apartment_type',
                  'country', 'percentage_discount', 'promotion_closing_date',
                  'number_of_bedrooms', 'number_of_toilets', 'default_image', 'total_property_cost',
                  'total_number_of_shares', 'price_per_share']

class PropertyMarketplaceSerializer (serializers.ModelSerializer):

    class Meta:
        model = Property
        fields = ['id', 'name', 'created_at', 'company_name', 'agent', 'description',
                  'apartment_type', 'address', 'city', 'state', 'apartment_type',
                  'country', 'percentage_discount', 'promotion_closing_date',
                  'number_of_bedrooms', 'number_of_toilets', 'default_image', 'total_property_cost',
                  'total_number_of_shares', 'price_per_share', 'image_album']

class PropertyTopdealsSerializer (serializers.ModelSerializer):

    image_album = MediaAlbumSerializer()
    class Meta:
        model = Property
        fields = ['id', 'name', 'created_at', 'company_name', 'agent', 'description',
                  'apartment_type', 'address', 'city', 'state', 'apartment_type',
                  'country', 'percentage_discount', 'promotion_closing_date',
                  'number_of_bedrooms', 'number_of_toilets', 'default_image', 'total_property_cost',
                  'total_number_of_shares', 'price_per_share', 'image_album']
class ShoppingCartPropertySerializer(serializers.ModelSerializer):

    class Meta:
        model = Property
        fields = ['id', 'company_name', 'name',
                  'price_per_share', 'total_number_of_shares', 'default_image']

class ShoppingCartSerializer(serializers.ModelSerializer):

    quantity = serializers.IntegerField()
    property = ShoppingCartPropertySerializer(read_only=True)
    property_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = ShoppingCart
        fields = ['quantity', 'property', 'property_id', 'created_at']


class RemoveShopingCartItemSerializer(serializers.Serializer):

    property_id = serializers.UUIDField(required=True)

class ScheduleSiteInspectionSerializer(serializers.Serializer):

    property_id = serializers.UUIDField()
    inspection_date = serializers.DateTimeField()

    def validate(self, attrs):
        inspection_date = attrs.get('inspection_date')

        if not greater_than_today (inspection_date) :
            raise ParseError('inspection_date must be a future date.')

        return attrs

class PropertyInspectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PropertyInspection
        fields = '__all__'

class PropertyInspectionQuerySerializer(serializers.Serializer):

    status = serializers.ChoiceField(choices=CHOICES_FOR_INSPECTION_STATUS, required=False)
    inspection_date = serializers.DateField(required=False)
    creation_date = serializers.DateField(required=False)
    class Meta:
        fields = ['creation_date', 'inspection_date', 'status']