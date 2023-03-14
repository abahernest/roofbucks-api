import json
from rest_framework import (views, permissions, parsers)
from rest_framework.response import Response
from django.db import transaction
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.db.models import Q

from .serializers import (NewPropertySerializer, StayPeriodSerializer,
                          PropertySerializer, ShoppingCartSerializer, PropertyTableSerializer, 
                          SimilarPropertyListSerializer, RemoveShopingCartItemSerializer,
                          ScheduleSiteInspectionSerializer, PropertyInspectionSerializer)
from authentication.permissions import IsAgent, IsCustomer
from .models import Property, ShoppingCart, PropertyInspection
from album.models import MediaFiles
from users.models import Company
from notifications.models import Notifications
from utils.pagination import CustomPagination
from utils.constants import (MAXIMUM_SIMILAR_PROPERTIES)
from utils.date import (convert_datetime_to_readable_date)

class NewPropertyAPIView(views.APIView):

    serializer_class = NewPropertySerializer
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]
    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def post(self, request):

        company = Company.objects.filter(user=request.user).first()
        if not company:
            return Response({
                'status_code': 403,
                'error': 'Complete business registration before uploading properties',
                'payload': ['Complete business registration before uploading properties']
            }, status=403)

        serializer = self.serializer_class(data= request.data)
        serializer.is_valid(raise_exception=True)

        # serializer.validated_data['agent'] = request.user

        with transaction.atomic():
            property=serializer.save(agent = request.user, company_name=company.registered_name, company=company)
            property = Property.objects.filter(id=property.id).values()[0]

            ## fetch media files
            property['images'] = MediaFiles.objects.filter(
                album=property['image_album_id']).values('image','id')
            # property['documents'] = MediaFiles.objects.filter(
            #     album=property['document_album_id']).values('document','id')

            ## notify agent
            notificationMessage = f'New Property Added. {property["name"]}'
            Notifications.new_entry(user= request.user, message=notificationMessage)

        return Response(property, status=200)



class StayPeriodAPIView(views.APIView):

    serializer_class = StayPeriodSerializer
    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def patch (self, request, property_id):

        properties = Property.objects.filter(id=property_id)
        if len(properties) <1:
            return Response({
                'status_code': 400,
                'error': 'No property with that ID',
                'payload': ['No property with that ID']}, status=400)

        property = properties[0]
        serializer = self.serializer_class(property, data=request.data)
        serializer.is_valid(raise_exception=True)

        if property.agent != request.user:
            return Response({
                'status_code': 400,
                'error': 'This resource belongs to another user',
                'payload': ['This resource belongs to another user']}, status=400)

        with transaction.atomic():
            serializer.save()

        return Response({'message': 'successful'}, status=200)


    def get (self, request, property_id):

        properties = Property.objects.filter(id=property_id)
        if len(properties) <1:
            return Response({
                'status_code': 400,
                'error': 'No property with that ID',
                'payload': ['No property with that ID']}, status=400)

        property = properties[0]
        if property.agent != request.user:
            return Response({
                'status_code': 400,
                'error': 'This resource belongs to another user',
                'payload': ['This resource belongs to another user']}, status=400)

        return Response(property.scheduled_stays, status=200)


    def delete(self, request, property_id, index_of_stay_period):

        properties = Property.objects.filter(id=property_id)
        if len(properties) < 1:
            return Response({'errors': ['No property with that ID']}, status=400)

        property = properties[0]
        if property.agent != request.user:
            return Response({'errors': ['This resource belongs to another user']}, status=400)

        try:
            property.scheduled_stays.pop(int(index_of_stay_period))
        except:
            return Response({
                'status_code': 400,
                'error': 'Scheduled stay Index out of range',
                'payload': ['Scheduled stay Index out of range']}, status=400)

        property.save()

        return Response(property.scheduled_stays, status=200)



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

    serializer_class = SimilarPropertyListSerializer
    pagination_class = CustomPagination


    def group_by_propertyID(self, cursor):
        "Return all rows from a cursor as a dict"
        ## add extra column to store array of images
        columns = [col[0] for col in cursor.description] + ['images']
        
        hashMap = {}
        output = []
        for row in cursor.fetchall():
            ## Break condition
            if len(output) > MAXIMUM_SIMILAR_PROPERTIES:
                break

            property_id = row[0]
            image = row[-1]

            if property_id not in hashMap:
    
                row += ( [image], ) ##concatenate tuple

                output.append(dict(zip(columns, row)))
                ## delete image property from output item
                del(output[-1]['image'])
                hashMap[property_id] = {'index':len(output)-1}
            else:
                index = hashMap[property_id]['index']
                images = output[index]['images'] 
                images.append(image)

        return output

    def get(self, request, property_id):

        properties = Property.objects.filter(id=property_id)
        if len(properties) < 1:
            return Response({
                'status_code': 400,
                'error': 'No property with that ID',
                'payload': ['No property with that ID']}, status=400)

        properties = Property.objects.filter(
            ~Q(id=property_id),
            name__icontains=properties[0].name
        )[:MAXIMUM_SIMILAR_PROPERTIES]

        for property in properties:
            out = property.get_images()
            setattr(property, 'images', out)

        serializer = self.serializer_class(properties, many=True)

        return Response(serializer.data, status=200)



class PropertyDetailView(views.APIView):

    serializer_class = PropertySerializer

    def get(self, request, property_id):

        properties = Property.objects.filter(id=property_id)
        if len(properties) < 1:
            return Response({
                'status_code': 400,
                'error': 'No property with that ID',
                'payload': ['No property with that ID']}, status=400)

        property = properties[0]

        if property.agent != request.user:
            return Response({
                'status_code': 400,
                'error': 'This resource belongs to another user',
                'payload': ['This resource belongs to another user']}, status=400)

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


class UpdatePropertyAPIView(views.APIView):

    serializer_class = NewPropertySerializer
    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def patch(self, request, property_id):

        properties = Property.objects.filter(id=property_id)
        if len(properties) < 1:
            return Response({
                'status_code': 400,
                'error': 'No property with that ID',
                'payload': ['No property with that ID']}, status=400)

        property = properties[0]
        if property.agent != request.user:
            return Response({
                'status_code': 400,
                'error': 'This resource belongs to another user',
                'payload': ['This resource belongs to another user']}, status=400)

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


class RemoveMediaView(views.APIView):

    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def delete(self, request, media_type, property_id, media_id):

        properties = Property.objects.filter(id=property_id)
        if len(properties) < 1:
            return Response({
                'status_code': 400,
                'error': 'No property with that ID',
                'payload': ['No property with that ID']}, status=400)

        property = properties[0]
        if property.agent != request.user:
            return Response({
                'status_code': 400,
                'error': 'This resource belongs to another user',
                'payload': ['This resource belongs to another user']}, status=400)

        ## Determine album ID of media file to delete
        album_id = None
        if media_type == 'image':
            album_id = property.image_album
        elif media_type == 'document':
            album_id = property.document_album
        else:
            return Response({
                'status_code': 400,
                'error': 'media_type must be either "image" or "document"',
                'payload': ['media_type must be either "image" or "document"']}, status=400)

        media_files = MediaFiles.objects.filter(id=media_id, album=album_id)
        if len(media_files) < 1:
            return Response({
                'status_code': 400,
                'error': 'No Media file with that ID',
                'payload': ['No Media file with that ID']}, status=400)

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

    

class ShoppingCartAPIView(views.APIView):

    permission_classes = [permissions.IsAuthenticated, IsCustomer]
    serializer_class = ShoppingCartSerializer

    def get(self, request):

        cart_items = ShoppingCart.objects.select_related('property').order_by('-created_at').filter(user=request.user)

        serializer = self.serializer_class(cart_items, many=True)
        return Response(serializer.data, status=200)


    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        property = Property.objects.filter(id=serializer.validated_data['property_id']).first()
        if not property:
            return Response({
                'status_code': 404,
                'error': 'Property with ID not found',
                'payload': ['Property with ID not found']}, status=404)

        cart = ShoppingCart.objects.filter(user=request.user, property=property).first()
        if cart:
            return Response({
                'status_code': 400,
                'error': 'Property Already in shopping cart',
                'payload': ['Property Already in shopping cart']}, status=400)

        if not property.total_number_of_shares:
            return Response({
                'status_code': 400,
                'error': 'Agent is yet to specify available number of shares.',
                'payload': ['Agent is yet to specify available number of shares.']},
                status=400)

        if serializer.validated_data['quantity'] > property.total_number_of_shares:
            return Response({
                'status_code': 400,
                'error': f'Quantity specified is more than available shares({property.total_number_of_shares})',
                'payload': [f'Quantity specified is more than available shares({property.total_number_of_shares})']},
                status=400)

        with transaction.atomic():
            cart = serializer.save(user= request.user, property=property)

        serializer = self.serializer_class(cart)
        return Response(serializer.data, status=200)



    def delete(self, request):

        serializer = RemoveShopingCartItemSerializer(data= request.data)
        serializer.is_valid(raise_exception=True)

        property_id = serializer.validated_data.get('property_id')
        cart_item = ShoppingCart.objects.filter(user=request.user, property_id=property_id).first()

        if not cart_item:
            return Response({
                'status_code': 400,
                'error': 'Item not found in cart for this user',
                'payload': ['Item not found in cart for this user']},
                status=400)

        with transaction.atomic():
            response = cart_item.delete()

        return Response({'message':'successful'}, status=200)


    def patch(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        property_id = serializer.validated_data.get('property_id')
        quantity = serializer.validated_data.get('quantity')

        cart_item = ShoppingCart.objects.filter(
            user=request.user, property_id=property_id).first()

        if not cart_item:
            return Response({
                'status_code': 400,
                'error': 'Item not found in cart for this user',
                'payload': ['Item not found in cart for this user']}, status=400)

        with transaction.atomic():
            cart_item.quantity = quantity
            cart_item.save()

        serializer = self.serializer_class(cart_item)

        return Response(serializer.data, status=200)



class CreateAndListSiteVisitAPIView (views.APIView):

    serializer_class = PropertyInspectionSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def post(self, request):

        serializer = ScheduleSiteInspectionSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            propertyInspectionObj = {}
            property_id = serializer.validated_data.get('property_id')
            inspection_date = serializer.validated_data.get('inspection_date')

            ## check for existence of property
            property = Property.objects.filter(id = property_id).first()
            if not property:
                return Response({
                    'status_code': 400,
                    'error': 'No proeprty with that ID',
                    'payload': ['No proeprty with that ID']}, status = 400)


            propertyInspectionObj = {
                'property': property,
                'company_name': property.company_name,
                'agent': property.agent,
                'agent_phone': property.agent.phone,
                'agent_firstname': property.agent.firstname,
                'agent_lastname': property.agent.lastname,
                'client': request.user,
                'client_firstname': request.user.firstname,
                'client_lastname': request.user.lastname,
                'inspection_date': inspection_date,
            }

            inspection_detail = PropertyInspection.objects.create(**propertyInspectionObj)
            serializer = self.serializer_class(inspection_detail)

            ##send notifications
            formatted_datetime = convert_datetime_to_readable_date(inspection_date)
            client_notification_message = f'Scheduled Site Visit for {property.company_name} at {formatted_datetime}'
            agent_notification_message = f'Scheduled Site Visit for {property.name} with ID {property.id} at {formatted_datetime}'

            Notifications.new_bulk_entry([
                {"user": request.user, "message": client_notification_message}, ## notify client
                {"user": property.agent, "message": agent_notification_message} ## notify agent
            ])

        return Response(serializer.data, status=200)

    
    def get(self, request):

        properties = PropertyInspection.objects.filter(client = request.user).all()
        serializer = self.serializer_class(properties, many=True)

        return Response(serializer.data, status = 200)



class CancelSiteVisitAPIView (views.APIView):

    serializer_class = PropertyInspectionSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def patch(self, request, visitation_id):

        inspectionObj = PropertyInspection.objects.filter(id= visitation_id, client = request.user).first()
        if not inspectionObj:
            return Response({
                'status_code': 400,
                'error': 'No record with this inspection Id',
                'payload': ['No record with this inspection Id']}, status=400)

        if inspectionObj.status != 'PENDING':
            return Response({
                'status_code': 400,
                'error': 'Can only cancel PENDING inspection ID',
                'payload': ['Can only cancel PENDING inspection ID']}, status=400)

        with transaction.atomic():
            inspectionObj.status = 'CANCELLED'
            inspectionObj.save()

            ## send notifications
            client_notification_message = f'Cancelled Site Visit for {inspectionObj.property.company_name}'
            agent_notification_message = f'{inspectionObj.client_firstname} {inspectionObj.client_lastname} cancelled site visit for {inspectionObj.property.name} with ID {inspectionObj.property.id}'

            Notifications.new_bulk_entry([
                {"user": request.user, "message": client_notification_message}, ## notify client
                {"user": inspectionObj.property.agent, "message": agent_notification_message} ## notify agent
            ])

        serializer = self.serializer_class(inspectionObj)

        return Response(serializer.data, status=200)



class AcceptAndRejectInspectionAPIView(views.APIView):

    serializer_class = PropertyInspectionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def patch(self, request, visitation_id, agent_action):

        global_status = None
        if agent_action.lower() == 'accept':
            global_status = "ACCEPTED"
        elif agent_action.lower() == 'reject':
            global_status = 'REJECTED'
        else:
            return Response({
                'status_code': 400,
                'error': "agent_action can only be 'accept' or 'reject'",
                'payload': ["agent_action can only be 'accept' or 'reject'"]}, status=400)

        inspectionObj = PropertyInspection.objects.filter(id=visitation_id, agent=request.user).first()
        if not inspectionObj:
            return Response({
                'status_code': 400,
                'error': 'No record with this inspection Id',
                'payload': ['No record with this inspection Id']}, status=400)

        if inspectionObj.status != 'PENDING':
            return Response({
                'status_code': 400,
                'error': f'Can only {agent_action} PENDING inspection',
                'payload': [f'Can only {agent_action} PENDING inspection']}, status=400)

        with transaction.atomic():
            inspectionObj.status = global_status
            inspectionObj.save()

            ## send notifications
            client_notification_message = f'Site Visit for {inspectionObj.property.company_name} has been {global_status.lower()} '
            agent_notification_message = f'{global_status.capitalize()} site visit for {inspectionObj.property.name} with ID {inspectionObj.property.id}'

            Notifications.new_bulk_entry([
                {"user": request.user, "message": client_notification_message}, ## notify client
                {"user": inspectionObj.property.agent, "message": agent_notification_message} ## notify agent
            ])

        serializer = self.serializer_class(inspectionObj)

        return Response(serializer.data, status=200)


class AgentPropertyInspectionsAPIView(views.APIView):

    serializer_class = PropertyInspectionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def get(self, request):

        query = {"agent":request.user}
        status = request.GET.get('status')

        if status in ['pending', 'accepted', 'rejected']:
            query['status'] = status.upper()

        inspectionObjs = PropertyInspection.objects.filter(**query)

        serializer = self.serializer_class(inspectionObjs, many=True)

        return Response(serializer.data, status=200)

