"""Business logic services for the accounts app.

AuthService exposes user registration and authentication helpers used by
the API views. JWTService centralizes token creation and rotation using
``rest_framework_simplejwt`` primitives.
"""

from .models import Profile, Role
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
import mimetypes

class AuthService:
    def register_user(self, username, email, password, role, profile_picture=None):
        """Register a new user with basic validation.

        Args:
            username (str): Desired username.
            email (str): User email address.
            password (str): Plain-text password.
            role (str): Role value (teacher|student|admin).
            profile_picture (File, optional): Uploaded profile image.

        Returns:
            Profile: The created user instance.

        Raises:
            ValueError: When the role is invalid or the profile picture
                does not meet validation requirements.
        """

        if role not in Role.values:
            raise ValueError("Invalid role. Must be one of: teacher, student, admin.")

        if profile_picture:
            mime_type, _ = mimetypes.guess_type(profile_picture.name)
            if not mime_type or not mime_type.startswith('image'):
                raise ValueError("Invalid file type. Only image files are allowed.")
            if profile_picture.size > 5 * 1024 * 1024:
                raise ValueError("File size exceeds the limit of 5MB.")

        user = Profile.objects.create_user(username=username, email=email, password=password, role=role)
        if profile_picture:
            user.profile_picture = profile_picture
            user.save()
        return user

    def login_user(self, username, password):
        """Authenticate a user by username and password.

        Returns the user instance when credentials are valid.

        Args:
            username (str): Username to authenticate.
            password (str): Plain-text password.

        Returns:
            Profile: Authenticated user instance.

        Raises:
            ValueError: If authentication fails.
        """

        user = Profile.objects.filter(username=username).first()
        if user and user.check_password(password):
            return user
        raise ValueError("Invalid username or password")

class JWTService:
    def generate_tokens(self, user):
        """Create an access/refresh token pair for a user.

        Args:
            user (Profile): User for whom to generate tokens.

        Returns:
            dict: Dictionary with ``access``, ``refresh`` and ``token_type``.
        """

        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'token_type': 'bearer',
        }

    def generate_token(self, user):
        """Return only an access token for compatibility.

        Args:
            user (Profile): User instance.

        Returns:
            str: Access token string.
        """

        return self.generate_tokens(user)['access']

    def refresh_access_token(self, refresh_token):
        """Validate a refresh token and return a new access token.

        Args:
            refresh_token (str): Refresh token string.

        Returns:
            dict: New token payload containing ``access`` and ``refresh``.

        Raises:
            ValueError: If the refresh token is invalid.
        """

        try:
            token = RefreshToken(refresh_token)
        except TokenError as exc:
            raise ValueError('Invalid refresh token') from exc

        return {
            'access': str(token.access_token),
            'refresh': str(token),
            'token_type': 'bearer',
        }

    def decode_token(self, token):
        """Decode an access or refresh token returning its payload.

        Args:
            token (str): Token string to decode.

        Returns:
            dict: Token payload.

        Raises:
            ValueError: If the token cannot be decoded.
        """

        try:
            return AccessToken(token).payload
        except TokenError:
            try:
                return RefreshToken(token).payload
            except TokenError as exc:
                raise ValueError('Invalid token') from exc
