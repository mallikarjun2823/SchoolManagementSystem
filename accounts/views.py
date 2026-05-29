"""Views for account management (registration, login, token refresh).

This module provides lightweight API views used to register new users,
authenticate existing users and rotate refresh tokens. The views are
intended for use by a REST client such as a frontend application.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ProfileCreateSerializer
from .services import AuthService, JWTService


class RegistrationView(APIView):
    """API endpoint that registers new users.

    Expects a JSON payload with ``username``, ``email``, ``password``,
    ``role`` and an optional ``profile_picture``. Returns the created
    user representation and JWT tokens on success.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Handle POST request to create a new user.

        Args:
            request (rest_framework.request.Request): Incoming request
                containing user registration data.

        Returns:
            rest_framework.response.Response: 201 with user and tokens, or
            400 with validation errors.
        """

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
    """API endpoint that authenticates users and returns tokens.

    Accepts ``username`` and ``password`` in the POST body and returns
    an access/refresh token pair when credentials are valid.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticate a user and return JWT tokens.

        Args:
            request (rest_framework.request.Request): Request containing
                ``username`` and ``password``.

        Returns:
            rest_framework.response.Response: 200 with tokens on success or
            400 with an error message on failure.
        """

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


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh') or request.data.get('refresh_token')
        if not refresh_token:
            return Response({'refresh': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tokens = JWTService().refresh_access_token(refresh_token)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(tokens, status=status.HTTP_200_OK)

