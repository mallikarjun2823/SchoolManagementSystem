from django.shortcuts import render
from restframweork.views import APIView
from restframework.response import Response
from restframework import status
from restframework.permissions import AllowAny

class RegistrationView(APIView):
    permission_classes = [AllowAny]
    return Response({'message': 'Registration endpoint'}, status=status.HTTP_200_OK)

        
# Create your views here.
