from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ProfileCreateSerializer
from .services import AuthService, JWTService


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ProfileCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = AuthService().register_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data.get('email', ''),
                password=serializer.validated_data['password'],
                role=serializer.validated_data['role'],
                profile_picture=serializer.validated_data.get('profile_picture'),
            )
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        tokens = JWTService().generate_tokens(user)
        return Response({
            'user': ProfileCreateSerializer(user).data,
            **tokens,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            errors = {}
            if not username:
                errors['username'] = ['This field is required.']
            if not password:
                errors['password'] = ['This field is required.']
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = AuthService().login_user(username, password)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        tokens = JWTService().generate_tokens(user)
        return Response({
            'user': {
                'username': user.username,
                'email': user.email,
                'role': user.role,
            },
            **tokens,
        }, status=status.HTTP_200_OK)

