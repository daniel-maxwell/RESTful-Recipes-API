"""
Database Models
"""

from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin
)

class UserManager(BaseUserManager):
    """Manager for user profiles."""

    def create_user(self, email, password=None, **extra_fields):
        """Create a new user, then save and return it."""

        # Create a new user model from email and extra fields
        user = self.model(email=email, **extra_fields)

        # Set (hashed) password for user
        user.set_password(password)

        # Save the user model to database
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True) # Email (must be unique)
    name = models.CharField(max_length=25) # Name of user
    is_active = models.BooleanField(default=True) # Default is True
    is_staff = models.BooleanField(default=False) # Default is False


    objects = UserManager() # User manager for user model

    USERNAME_FIELD = 'email' # Username is email address

# from django.db import models

# Create your models here.
