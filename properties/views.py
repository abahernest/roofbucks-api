import json
from rest_framework import (views, permissions, parsers)
from rest_framework.response import Response
from django.db import transaction
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.db.models import Q

from .serializers import (NewPropertySerializer, StayPeriodSerializer,
                          PropertySerializer, ShoppingCartSerializer, PropertyTableSerializer)
from authentication.permissions import IsAgent, IsCustomer
from .models import Property, ShoppingCart
from album.models import MediaFiles
from users.models import Company
from utils.pagination import CustomPagination
from utils.constants import (MAXIMUM_SIMILAR_PROPERTIES)

class NewPropertyAPIView(views.APIView):

    serializer_class = NewPropertySerializer
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]
    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def post(self, request):
        
        try:
            company = Company.objects.filter(user=request.user).first()
            if not company:
                return Response({'errors':['Complete business registration before uploading properties']}, status=403)

            serializer = self.serializer_class(data= request.data)
            serializer.is_valid(raise_exception=True)
            
            # serializer.validated_data['agent'] = request.user

            with transaction.atomic():
                property=serializer.save(agent = request.user, company_name=company.registered_name, company=company)
                property = Property.objects.filter(id=property.id).values()[0]
                
                ## fetch media files
                property['images'] = MediaFiles.objects.filter(
                    album=property['image_album_id']).values('image','id')
                property['documents'] = MediaFiles.objects.filter(
                    album=property['document_album_id']).values('document','id')

            return Response(property, status=200)

        except Exception as e:
            return Response({'errors': e.args}, status=500)

class StayPeriodAPIView(views.APIView):

    serializer_class = StayPeriodSerializer
    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def patch (self, request, property_id):
        
        try:
            properties = Property.objects.filter(id=property_id)
            if len(properties) <1:
                return Response({'errors': ['No property with that ID']}, status=400)

            property = properties[0]    
            serializer = self.serializer_class(property, data=request.data)
            serializer.is_valid(raise_exception=True)
            
            if property.agent != request.user:
                return Response({'errors': ['This resource belongs to another user']}, status=400)

            with transaction.atomic():
                serializer.save()

            return Response({'message': 'successful'}, status=200)

        except Exception as e:
            return Response({'errors': e.args}, status=500)

    def get (self, request, property_id):

        try:
            properties = Property.objects.filter(id=property_id)
            if len(properties) <1:
                return Response({'errors': ['No property with that ID']}, status=400)
            
            property = properties[0]
            if property.agent != request.user:
                return Response({'errors': ['This resource belongs to another user']}, status=400)

            return Response(property.scheduled_stays, status=200)

        except Exception as e:
            return Response({'errors': e.args}, status=500)

    def delete(self, request, property_id, index_of_stay_period):
         
        try:
            properties = Property.objects.filter(id=property_id)
            if len(properties) < 1:
                return Response({'errors': ['No property with that ID']}, status=400)

            property = properties[0]
            if property.agent != request.user:
                return Response({'errors': ['This resource belongs to another user']}, status=400)

            try:
                property.scheduled_stays.pop(int(index_of_stay_period))
            except:
                return Response({'errors': ['Scheduled stay Index out of range']}, status=400)

            property.save()

            return Response(property.scheduled_stays, status=200)

        except Exception as e:
            return Response({'errors': e.args}, status=500)


class PropertyListView(ReadOnlyModelViewSet):

    filter_backends = [SearchFilter]
    serializer_class = PropertyTableSerializer
    permission_classes = [permissions.IsAuthenticated, IsAgent]
    search_fields = ['name', 'id']
    pagination_class = CustomPagination

    def get_queryset(self):
        user_id = self.request.user.id
        return Property.objects.filter(
            agent=user_id
        ).order_by('-created_at')


class SimilarPropertyView(views.APIView):

    serializer_class = PropertySerializer
    pagination_class = CustomPagination

    def get(self, request, property_id):
        try:
            properties = Property.objects.filter(id=property_id)
            if len(properties) < 1:
                return Response({'errors': ['No property with that ID']}, status=400)
            
            properties = Property.objects.filter(
                ~Q(id=property_id), 
                name__icontains = properties[0].name
                )[:MAXIMUM_SIMILAR_PROPERTIES]

            for property in properties:
                property.get_images()
                property.get_documents()

            serializer = self.serializer_class(properties, many=True)

            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({'errors': e.args}, status=500)


class PropertyDetailView(views.APIView):

    serializer_class = PropertySerializer

    def get(self, request, property_id):
        
        try:
            properties = Property.objects.filter(id=property_id)
            if len(properties) < 1:
                return Response({'errors': ['No property with that ID']}, status=400)

            property = properties[0]

            if property.agent != request.user:
                return Response({'errors': ['This resource belongs to another user']}, status=400)

            serializer = self.serializer_class(property)


            # fetch media files
            output = serializer.data
            output['images'] = MediaFiles.objects.filter(
                album=property.image_album_id).values('image')

            output['documents'] = MediaFiles.objects.filter(
                album=property.document_album).values('document')

            ## fetcy agent information and company information

            number_of_listed_properties= Property.objects.filter(
                agent=property.agent, moderation_status='APPROVED').count()

            output['agent'] = {
                'id': property.agent_id,
                'firstname': property.agent.firstname,
                'lastname': property.agent.lastname,
                'display_photo': property.agent.display_photo.url if property.agent.display_photo else None,
                'natinality': property.agent.nationality,
                'email': property.agent.email,
                'phone': property.agent.phone,
                'agency': property.company_name,
                'listed_properties': number_of_listed_properties
            }

            return Response(output, status=200)

        except Exception as e:
            return Response({'errors': e.args}, status=500)

class UpdatePropertyAPIView(views.APIView):

    serializer_class = NewPropertySerializer
    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def patch(self, request, property_id):

        try:
            properties = Property.objects.filter(id=property_id)
            if len(properties) < 1:
                return Response({'errors': ['No property with that ID']}, status=400)

            property = properties[0]
            if property.agent != request.user:
                return Response({'errors': ['This resource belongs to another user']}, status=400)

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
            return Response(property, status=200)

        except Exception as e:
            return Response({'errors': e.args}, status=500)

class RemoveMediaView(views.APIView):

    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def delete(self, request, media_type, property_id, media_id):

        try:
            properties = Property.objects.filter(id=property_id)
            if len(properties) < 1:
                return Response({'errors': ['No property with that ID']}, status=400)

            property = properties[0]
            if property.agent != request.user:
                return Response({'errors': ['This resource belongs to another user']}, status=400)
            
            ## Determine album ID of media file to delete
            album_id = None
            if media_type == 'image':
                album_id = property.image_album
            elif media_type == 'document':
                album_id = property.document_album
            else:
                return Response({'errors': ['media_type must be either "image" or "document"']}, status=400)

            media_files = MediaFiles.objects.filter(id=media_id, album=album_id)
            if len(media_files) < 1:
                return Response({'errors': ['No Media file with that ID']}, status=400)

            mediafile = media_files[0]
            filename = None
            with transaction.atomic():
                mediafile.delete()
                if media_type =='image': 
                    filename = mediafile.image.name
                    mediafile.delete_image_from_storage()
                else : 
                    filename = mediafile.document.name
                    mediafile.delete_document_from_storage()
                ## notice that MediaAlbum is not deleted even if media is last item in album

            return Response({'message': f'successfully deleted {filename}'}, status=200)

        except Exception as e:
            return Response({'errors': e.args}, status=500)
    

class ShoppingCartAPIView(views.APIView):

    permission_classes = [permissions.IsAuthenticated, IsCustomer]
    serializer_class = ShoppingCartSerializer

    def get(self, request):

        try:
            cart_items = ShoppingCart.objects.select_related('property').filter(user=request.user)
            
            for item in cart_items:

                images = MediaFiles.objects.filter(album = item.property.image_album)
                if len(images)>0:
                    property = item.property
                    setattr(property, 'images', images)
                else:
                    property = item.property
                    setattr(property, 'images', None)

            serializer = self.serializer_class(cart_items, many=True)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({'errors':e.args}, status=500)

    def post(self, request):
        
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            property = Property.objects.filter(id=serializer.validated_data['property_id']).first()
            if not property:
                return Response({'errors':['Property with ID not found']}, status=404)

            cart = ShoppingCart.objects.filter(user=request.user, property=property).first()
            if cart:
                return Response({'errors': ['Property Already in shopping cart']})

            if not property.total_number_of_shares:
                return Response({'errors':['Agent is yet to specify available number of shares.']}, status=400)

            if serializer.validated_data['quantity'] > property.total_number_of_shares:
                return Response({'errors':[f'Quantity specified is more than available shares({property.total_number_of_shares})']})
            
            with transaction.atomic():
                cart = serializer.save(user= request.user, property=property)
            
            # property.get_images()
            # setattr(cart, "property", property)
            # serializer = self.serializer_class(cart)
            return Response({'message':'successful'}, status=200)

        except Exception as e:
            return Response({'errors': e.args}, status=500)

