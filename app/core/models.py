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

        if not email:
            raise ValueError('An email address is required to create a user.')

        # Create a new user model from email and extra fields
        usr = self.model(email=self.normalize_email(email), **extra_fields)

        # Set (hashed) password for user
        usr.set_password(password)

        # Save the user model to database
        usr.save()

        return usr

    def create_superuser(self, email, password):
        """Create, save, and return a new superuser."""

        # Create a new user with email and password
        usr = self.create_user(email, password)

        # Set user as superuser and staff
        usr.is_superuser = True
        usr.is_staff = True

        # Save the user model to database
        usr.save()

        return usr

class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)  # Email (unique)
    name = models.CharField(max_length=25)  # Name of user
    is_active = models.BooleanField(default=True)  # Default is True
    is_staff = models.BooleanField(default=False)  # Default is False

    objects = UserManager()  # User manager for user model

    USERNAME_FIELD = 'email'  # Username is email address
