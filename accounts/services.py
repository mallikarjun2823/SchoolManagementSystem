from .models import Profile, Role
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
import mimetypes

class AuthService:
    def register_user(self, username, email, password, role, profile_picture=None):
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
        user = Profile.objects.filter(username=username).first()
        if user and user.check_password(password):
            return user
        raise ValueError("Invalid username or password")

class JWTService:
    def generate_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'token_type': 'bearer',
        }

    def generate_token(self, user):
        return self.generate_tokens(user)['access']

    def refresh_access_token(self, refresh_token):
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
        try:
            return AccessToken(token).payload
        except TokenError:
            try:
                return RefreshToken(token).payload
            except TokenError as exc:
                raise ValueError('Invalid token') from exc
