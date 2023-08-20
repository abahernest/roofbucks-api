from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import views
from rest_framework.filters import SearchFilter
from rest_framework import (parsers,permissions,authentication)
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.db import transaction
from rest_framework.decorators import permission_classes
from django.db.models import Avg, Count

from .models import User, Company, Review
from album.models import MediaFiles
from properties.models import Property
from .serializers import (UpdateProfileSerializer, CreateCompanySerializer,
                          AddBankInfoSerializer, BusinessProfileSerializer,
                          AgentListSerializer, ReviewsSerializer, AccountSettingsSerializer)
from utils.pagination import CustomPagination
from utils.constants import (NUMBER_OF_REVIEWS_TO_DISPLAY)
from authentication.permissions import IsCustomer, IsAgent


class Profile(views.APIView):

    serializer_class = UpdateProfileSerializer
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]

    def patch(self,request):

        user_id = request.user.id
        user = User.objects.get(id=user_id)

        serializer = self.serializer_class(user, data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            serializer.save()
            # user.refresh_from_db()
            user = User.objects.filter(id=user_id).values('id','firstname', 'lastname', 'date_of_birth', 'email', 'address',
                                       'city', 'country', 'phone', 'identity_document_type',
                                       'identity_document_number', 'identity_document_expiry_date',
                                       'display_photo', 'proof_of_address_document', 'identity_document_album'
                                       )[0]
            documents = None
            if user['identity_document_album']:
                documents = MediaFiles.objects.filter(
                    album=user['identity_document_album']).values('id', 'document')

            user['identity_documents'] = documents

            return Response(user, status=200)


    def get(self,request):

        user_id = request.GET.get('user_id') if request.GET.get('user_id') else request.user.id
        user = User.objects.get(id=user_id)

        serializer = self.serializer_class(user)

        return Response(serializer.data, status=200)


class AccountSettingsView(views.APIView):
    serializer_class = AccountSettingsSerializer
    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def patch(self, request):

        serializer = self.serializer_class(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            serializer.save()

            return Response(serializer.data, status=200)

    def get(self, request):

        user = request.user
        company = user.get_company()

        account_settings = {
            'display_name': user.display_name,
            'agency_display_name': company.display_name,
            'agency_website': company.website
        }

        return Response(account_settings, status=200)

class BusinessProfileView(views.APIView):

    serializer_class = BusinessProfileSerializer

    def get(self, request, user_id):

        user = User.objects.filter(id=user_id).all()
        if len(user) == 0:
            return Response({
                'status_code': 400,
                'error': 'User not found',
                'payload': ['User not found']}, status=400)

        ## attach company info to user object
        user = user[0]
        company = user.get_company()

        if not company:
            return Response({
                'status_code': 404,
                'error': 'User has no company',
                'payload': ['User has no company']
            }, status=404)

        # attach properties to user object
        order = '-created_at'
        if request.GET.get('order_by') == 'created_at':
            order = 'created_at'

        properties = Property.objects.filter(agent=user_id).all().order_by(order)

        for property in properties:
            property.get_images()
            property.get_documents()

        setattr(user, 'properties', properties)

        ## attach reviews to user object
        reviews = Review.objects.filter(company=company)[:NUMBER_OF_REVIEWS_TO_DISPLAY].all()
        rating = reviews.aggregate(Avg('rating'))

        setattr(user, 'rating', rating['rating__avg'])
        setattr(user, 'reviews', reviews)

        serializer = self.serializer_class(user)

        return Response(serializer.data, status=200)

class CreateCompany(views.APIView):

    serializer_class = CreateCompanySerializer
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        reference_number = request.data.get('reference_number', '')

        company_objects = Company.objects.filter(
            reference_number=reference_number, user = request.user)

        if len(company_objects) == 0:
            return Response({
                'status_code': 400,
                'error': "reference number not found. validate your company registration number again",
                "payload": ["reference number not found. validate your company registration number again"]}, status=400)

        if not company_objects[0].is_verified:
            return Response({
                'status_code': 400,
                'error': "verify company registration number",
                "payload": ["verify company registration number"]}, status=400)

        serializer = self.serializer_class(company_objects[0], data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            serializer.save()

            user = request.user
            user.stages_of_profile_completion['business'] = True
            user.save()

        return Response(serializer.data, status=200)



class AddBankInformation(views.APIView):

    serializer_class = AddBankInfoSerializer
    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def patch(self, request):

        company_objects = Company.objects.filter(user=request.user)

        if len(company_objects) ==0:
            return Response({
                "status_code": 400,
                "error": "User hasn't registered a business.",
                "payload": ["User hasn't registered a business."]}, status=400)

        serializer = self.serializer_class(company_objects[0], data=request.data )
        serializer.is_valid(raise_exception=True)
        output = serializer.save()
        return Response(output, status=200)



class AgentListView(ReadOnlyModelViewSet):

    filter_backends = [SearchFilter]
    serializer_class = AgentListSerializer
    search_fields = ['firstname', 'lastname']
    pagination_class = CustomPagination

    def get_queryset(self):
        return User.objects.filter(
            role='AGENT',
            is_verified=True,
            stages_of_profile_completion__profile=True,
            stages_of_profile_completion__business=True,
            stages_of_profile_completion__billing=True,
            stages_of_kyc_verification__profile=True,
            stages_of_kyc_verification__business=True
        ).order_by('-created_at')


class ReviewListView(views.APIView):

    serializer_class = ReviewsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, company_id):

        reviews = Review.objects.filter(company=company_id)

        serializer = self.serializer_class(reviews, many=True)

        return Response(serializer.data, status=200)



class ReviewCreateView(views.APIView):

    serializer_class = ReviewsSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def post(self, request, company_id):

        company = Company.objects.filter(id=company_id)

        if len(company) == 0:
            return Response({
                "status_code": 400,
                "error": "Company not found",
                "payload": ["Company not found"]}, status=400)

        if company[0].user == request.user:
            return Response({
                "status_code": 400,
                "error": "Cannot review this company as it belongs to this user",
                'payload': ["Cannot review this company as it belongs to this user"]}, status=403)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            serializer.save(reviewer = request.user, company = company[0])

        return Response(serializer.data, status=200)

