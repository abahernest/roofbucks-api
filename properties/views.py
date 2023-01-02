import json
from rest_framework import (views, permissions, parsers)
from rest_framework.response import Response
from django.db import transaction
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.exceptions import ParseError

from .serializers import (NewPropertySerializer, StayPeriodSerializer, PropertySerializer)
from authentication.permissions import IsAgent
from .models import Property, MediaFiles, MediaAlbum
from utils.pagination import CustomPagination
from utils.constants import (ALLOWABLE_NUMBER_OF_DOCUMENTS, ALLOWABLE_NUMBER_OF_IMAGES)

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
                album=property['image_album_id']).values('image','id')
            property['documents'] = MediaFiles.objects.filter(
                album=property['document_album_id']).values('document','id')

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

    def patch(self, request, property_id):

        properties = Property.objects.filter(id=property_id)
        if len(properties) < 1:
            return Response({'message': 'No property with that ID'}, status=400)

        property = properties[0]
        if property.agent != request.user:
            return Response({'message': 'This resource belongs to another user'}, status=400)

        serializer = self.serializer_class(property, data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            serializer.save()

        property = Property.objects.filter(id=property.id).values()[0]
        
        # fetch media files
        property['images'] = MediaFiles.objects.filter(
            album=property['image_album_id']).values('image', 'id')
        property['documents'] = MediaFiles.objects.filter(
            album=property['document_album_id']).values('document', 'id')
        return Response( property , status=200)