"""
Serializers for User API View
"""

from django.contrib.auth import (
    get_user_model as user_model,
    authenticate,
)
from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User object"""

    # Meta class is used to configure the serializer
    class Meta:
        model = user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    # Override the create function to create a user with a hashed password
    def create(self, validated_data):
        """Create a new user with a hashed password and return it"""
        return user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        # Remove the password from the validated data
        password = validated_data.pop('password', None)

        # Update the user with the validated data
        user = super().update(instance, validated_data)

        # If a password was provided, set it
        if password:
            user.set_password(password)
            user.save()

        return user

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the User Authentication token"""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    # Validate the user credentials
    def validate(self, attributes):
        """Validate and authenticate the user"""

        # Retrieve and store the email and password from the attributes
        email = attributes.get('email')
        password = attributes.get('password')

        # Authenticate the user
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )

        # If the authentication fails, raise an error (translates to 400 Bad Request)
        if not user:
            msg = _('System was not able to authenticate with the credentials provided')
            raise serializers.ValidationError(msg, code='authorization')

        # Set the user attribute so that it can be accessed in the view
        attributes['user'] = user
        return attributes
