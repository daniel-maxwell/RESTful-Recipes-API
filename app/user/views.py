"""
Views for the User API
"""
from rest_framework import generics, authentication, permissions
from rest_framework.settings import api_settings
from rest_framework.authtoken.views import ObtainAuthToken

from user.serializers import UserSerializer, AuthTokenSerializer

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for a user"""
    # Set the serializer class to the AuthTokenSerializer
    serializer_class = AuthTokenSerializer

    # Set the renderer classes to the default renderer classes
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManagerUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer

    # Set the authentication classes to the token authentication class
    authentication_classes = (authentication.TokenAuthentication,)

    # Set the permission classes to the IsAuthenticated class
    permission_classes = (permissions.IsAuthenticated,)

    # Override the get_object function to return the authenticated user
    def get_object(self):
        """Retrieve and return the authenticated user"""
        return self.request.user
