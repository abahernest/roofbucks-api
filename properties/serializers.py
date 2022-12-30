from rest_framework import serializers
from .models import Property, MediaAlbum, MediaFiles


class MediaFilesSerializer (serializers.ModelSerializer):

    class Meta:
        model = MediaFiles
        fields = ['image', 'document']


class MediaAlbumSerializer (serializers.ModelSerializer):

    media = MediaFilesSerializer(many=True, read_only=True)

    class Meta:
        model = MediaAlbum
        fields = ['media']


class NewPropertySerializer (serializers.ModelSerializer):

    def validate_file_extension(value):
        if value.content_type not in ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']:
            raise serializers.ValidationError(
                'Only PDF, JPG, JPEG, PNG files are allowed')

    def validate_file_size(value):
        max_size = 8388608
        if value.size > max_size:
            raise serializers.ValidationError('Maximum file size is 8MB')

    image_album = MediaAlbumSerializer(read_only=True)
    document_album = MediaAlbumSerializer(read_only=True)

    agent = serializers.IntegerField(required=False) ## disabled it here so agent_id can be passed in the view.py file
    images = serializers.ListField(
        child= serializers.ImageField(
            allow_empty_file=False,
            max_length = 256,
            validators=[validate_file_size]
            ),
        write_only= True,
        required=False,
        min_length=1,
        max_length=5
    )
    documents = serializers.ListField(
        child=serializers.FileField(
            allow_empty_file=False, 
            max_length=256,
            validators=[validate_file_extension, validate_file_size]
            ),
        write_only=True,
        required=False,
        min_length=1,
        max_length=6
    )

    class Meta:
        model = Property
        fields = '__all__'
        extra_kwargs = {'images': {'write_only': True},
                        'documents': {'write_only': True}}

    def validate(self, attrs):
        benefits = attrs.get('benefits')
        amenities = attrs.get('amenities')
        cross_streets = attrs.get('cross_streets')
        landmarks = attrs.get('landmarks')
        scheduled_stays = attrs.get('scheduled_stays')

        if benefits:
            attrs['benefits'] = benefits.strip().split(',')

        if amenities:
            attrs['amenities'] = amenities.strip().split(',')

        if cross_streets:
            attrs['cross_streets'] = cross_streets.strip().split(',')

        if landmarks:
            attrs['landmarks'] = landmarks.strip().split(',')

        if scheduled_stays:
            final_scheduled_stays = []

            ## use ',,' to seperate stay periods and ',' to seperate start and end date
            scheduled_stays = scheduled_stays.strip().split(',,')

            for stay_period in scheduled_stays:
                final_scheduled_stays.append(stay_period.split(','))

            attrs['scheduled_stays'] = final_scheduled_stays

        return attrs
            
    def create(self, validated_data):

        media_files_array = []

        uploaded_images = validated_data.get('images')
        uploaded_documents = validated_data.get('documents')

        if not (uploaded_documents or uploaded_images):
            return Property.objects.create(**validated_data)
        
        image_album, document_album = None, None
        
        if uploaded_images:
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

        MediaFiles.objects.bulk_create(media_files_array)


        property = Property.objects.create(
            **validated_data,
            image_album=image_album,
            document_album=document_album)

        return property


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
