from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import views
from rest_framework import (parsers,permissions,authentication)

from .models import User, Company
from .serializers import (UpdateProfileSerializer, CreateCompanySerializer, AddBankInfoSerializer)


class Profile(views.APIView):

    serializer_class = UpdateProfileSerializer
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]

    def patch(self,request):

        user_id = request.user.id
        user = User.objects.get(id=user_id)

        serializer = self.serializer_class(user, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data, status=200)

    def get(self,request):

        user_id = request.GET.get('user_id') if request.GET.get('user_id') else request.user.id
        user = User.objects.get(id=user_id)
        
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
            return Response({"errors":["reference number not found. validate your company registration number again"]}, status=400)

        if not company_objects[0].is_verified:
            return Response({"errors": ["verify company registration number"]}, status=400)

        serializer = self.serializer_class(company_objects[0], data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data, status=200)


class AddBankInformation(views.APIView):

    serializer_class = AddBankInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):

        company_objects = Company.objects.filter(user=request.user)

        if len(company_objects) ==0:
            return Response({ "errors": ["User hasn't registered a business."]}, status=400)

        serializer = self.serializer_class(company_objects[0], data=request.data )
        serializer.is_valid(raise_exception=True)
        output = serializer.save()
        return Response(output, status=200)