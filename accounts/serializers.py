from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Profile, Role
import mimetypes


class ProfileCreateSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)

    def validate_role(self, value):
        if value not in Role.values:
            raise serializers.ValidationError("Invalid role. Must be one of: teacher, student, admin.")
        return value

    def validate_profile_picture(self, value):
        if value:
            mime_type, _ = mimetypes.guess_type(value.name)
            if not mime_type or not mime_type.startswith('image'):
                raise serializers.ValidationError("Invalid file type. Only image files are allowed.")
            if value.size > 5 * 1024 * 1024:  # Limit file size to 5MB
                raise serializers.ValidationError("File size exceeds the limit of 5MB.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Profile.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'password', 'role', 'profile_picture', 'created_at']
        read_only_fields = ['id', 'created_at']
    
