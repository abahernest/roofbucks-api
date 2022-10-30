from rest_framework.response import Response
from django.http import JsonResponse

def profile(request):
    return JsonResponse("Profile Endpoint", safe=False)


