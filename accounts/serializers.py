"""Serializers for the accounts app.

Contains the serializer used to create and validate `Profile` objects
via the registration API.
"""

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Profile, Role
import mimetypes


class ProfileCreateSerializer(ModelSerializer):
    """Serializer for creating user profiles.

    This serializer validates the provided role and optional profile
    picture, and creates the user with a hashed password.
    """

    password = serializers.CharField(write_only=True)

    def validate_role(self, value):
        """Validate that the role is one of the allowed values.

        Args:
            value (str): Role value submitted by the client.

        Returns:
            str: The validated role value.

        Raises:
            serializers.ValidationError: If the value is not a valid role.
        """

        if value not in Role.values:
            raise serializers.ValidationError("Invalid role. Must be one of: teacher, student, admin.")
        return value

    def validate_profile_picture(self, value):
        """Validate uploaded profile picture file type and size.

        Args:
            value (UploadedFile): Uploaded file object.

        Returns:
            UploadedFile: The same file object when valid.

        Raises:
            serializers.ValidationError: If the file is not a valid image
                or exceeds the size limit.
        """

        if value:
            mime_type, _ = mimetypes.guess_type(value.name)
            if not mime_type or not mime_type.startswith('image'):
                raise serializers.ValidationError("Invalid file type. Only image files are allowed.")
            if value.size > 5 * 1024 * 1024:  # Limit file size to 5MB
                raise serializers.ValidationError("File size exceeds the limit of 5MB.")
        return value

    def create(self, validated_data):
        """Create a new `Profile` with a hashed password.

        Args:
            validated_data (dict): Data validated by the serializer.

        Returns:
            Profile: The newly created user instance.
        """

        password = validated_data.pop('password')
        user = Profile.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'password', 'role', 'profile_picture', 'created_at']
        read_only_fields = ['id', 'created_at']
    
