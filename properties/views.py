from rest_framework import (views, permissions, parsers)
from rest_framework.response import Response
from django.db import transaction
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.exceptions import ParseError

from .serializers import (NewPropertySerializer, StayPeriodSerializer, PropertySerializer)
from authentication.permissions import IsAgent
from .models import Property, MediaFiles
from utils.pagination import CustomPagination

class NewPropertyAPIView(views.APIView):

    serializer_class = NewPropertySerializer
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]
    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def post(self, request):
        
        serializer = self.serializer_class(data= request.data)
        serializer.is_valid(raise_exception=True)

        serializer.validated_data['agent'] = request.user

        with transaction.atomic():
            property=serializer.save()
            property = Property.objects.filter(id=property.id).values()[0]
            
            ## fetch media files
            property['images'] = MediaFiles.objects.filter(
                album=property['image_album_id']).values('image')
            property['documents'] = MediaFiles.objects.filter(
                album=property['document_album_id']).values('document')

        return Response( property, status=200)


class StayPeriodAPIView(views.APIView):

    serializer_class = StayPeriodSerializer
    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def patch (self, request, property_id):
        
        properties = Property.objects.filter(id=property_id)
        if len(properties) <1:
            return Response({'message':'No property with that ID'}, status=400)

        property = properties[0]    
        serializer = self.serializer_class(property, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if property.agent != request.user:
            return Response({'message':'This resource belongs to another user'}, status=400)

        with transaction.atomic():
            serializer.save()

        return Response( {'message':'successful'}, status=200)

    def get (self, request, property_id):

        properties = Property.objects.filter(id=property_id)
        if len(properties) <1:
            return Response({'message':'No property with that ID'}, status=400)
        
        property = properties[0]
        if property.agent != request.user:
            return Response({'message':'This resource belongs to another user'}, status=400)

        return Response(property.scheduled_stays, status=200)

    def delete(self, request, property_id, index_of_stay_period):
         
        properties = Property.objects.filter(id=property_id)
        if len(properties) < 1:
            return Response({'message': 'No property with that ID'}, status=400)

        property = properties[0]
        if property.agent != request.user:
            return Response({'message': 'This resource belongs to another user'}, status=400)

        try:
            property.scheduled_stays.pop(int(index_of_stay_period))
        except:
            return Response({'message': 'Scheduled stay Index out of range'}, status=400)

        property.save()

        return Response(property.scheduled_stays, status=200)


class PropertyListView(ReadOnlyModelViewSet):

    filter_backends = [SearchFilter]
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated, IsAgent]
    search_fields = ['name', 'id']
    pagination_class = CustomPagination

    def get_queryset(self):
        user_id = self.request.user.id
        return Property.objects.filter(
            agent=user_id
        ).order_by('-created_at')


class PropertyDetailView(views.APIView):

    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def get(self, request, property_id):
        
        properties = Property.objects.filter(id=property_id)
        if len(properties) < 1:
            return Response({'message': 'No property with that ID'}, status=400)

        property = properties[0]

        if property.agent != request.user:
            return Response({'message': 'This resource belongs to another user'}, status=400)

        serializer = self.serializer_class(property)


        # fetch media files
        output = serializer.data
        output['images'] = MediaFiles.objects.filter(
            album=property.image_album_id).values('image')

        output['documents'] = MediaFiles.objects.filter(
            album=property.document_album).values('document')
            
        return Response(output, status=200)

class UpdatePropertyAPIView(views.APIView):

    serializer_class = NewPropertySerializer
    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def partial_property_update(self, instance, validated_data):

        # count existing images and documents for this property
        total_images_uploaded, total_documents_uploaded = len(
            instance.get_images()), len(instance.get_documents())

        updatable_fields = {}
        for key in validated_data:
            if key in ['agent', 'image_album', 'document_album', 'moderation_status']:
                raise ParseError('Attempting to change Fixed Values')

            if key == 'images':
                media_files_array = []
                image_album = instance.image_album

                # fetch count of remaining allowable number of images
                remaining_number_of_images = ALLOWABLE_NUMBER_OF_IMAGES - total_images_uploaded
                # remaining_number_of_documents= ALLOWABLE_NUMBER_OF_DOCUMENTS - total_document_uploaded

                # ensure image uploaded doesn't exceed allowable number
                uploaded_images = validated_data.pop('images')
                if total_images_uploaded > ALLOWABLE_NUMBER_OF_IMAGES:
                    return ParseError('Exceeded alloted number of images. Delete existing images for this Property')
                elif total_images_uploaded == 0:
                    image_album = MediaAlbum.objects.create()
                elif remaining_number_of_images < len(uploaded_images):
                    return ParseError(f'Only {remaining_number_of_images} slots left for images')

                for image in uploaded_images:
                    media_files_array.append(
                        MediaFiles(album=image_album, image=image, media_type='IMAGE'))

                MediaFiles.objects.bulk_create(media_files_array)
                updatable_fields['image_album'] = image_album

            elif key == 'documents':
                media_files_array = []
                document_album = instance.document_album

                # fetch count of remaining allowable number of images
                remaining_number_of_documents = ALLOWABLE_NUMBER_OF_DOCUMENTS - total_documents_uploaded

                # ensure image uploaded doesn't exceed allowable number
                uploaded_documents = validated_data.pop('documents')
                if total_documents_uploaded > ALLOWABLE_NUMBER_OF_DOCUMENTS:
                    return ParseError('Exceeded alloted number of documents. Delete existing documents for this Property')
                elif total_documents_uploaded == 0:
                    document_album = MediaAlbum.objects.create()
                elif remaining_number_of_documents < len(uploaded_documents):
                    return ParseError(f'Only {remaining_number_of_documents} slots left for documents')

                for document in uploaded_documents:
                    media_files_array.append(
                        MediaFiles(album=document_album, document=document, media_type='DOCUMENT'))

                MediaFiles.objects.bulk_create(media_files_array)
                updatable_fields['document_album'] = document_album

            elif key == 'scheduled_stays':
                updatable_fields[key] = json.parse()
            else:
                updatable_fields[key] = validated_data.get(key)

        print('UPDATABLE', updatable_fields)
        return Property.objects.filter(id=instance.id) .update(**updatable_fields)

    def patch(self, request, property_id):

        properties = Property.objects.filter(id=property_id)
        if len(properties) < 1:
            return Response({'message': 'No property with that ID'}, status=400)

        property = properties[0]
        if property.agent != request.user:
            return Response({'message': 'This resource belongs to another user'}, status=400)

        serializer = self.serializer_class( data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            self.partial_property_update(property, serializer.data)

        return Response({'message':'output'}, status=200)