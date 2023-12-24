"""
Database Models
"""

from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin
                                        )
from django.conf import settings


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


class Recipe(models.Model):
    """The Recipe model."""

    # User that created the recipe
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    # Title, description, prep time, price, link and associated tags
    title = models.CharField(max_length=255)
    description = models.TextField()
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        """Returns the string representation of the recipe."""
        return self.title


class Ingredient(models.Model):
    """The Ingredient model."""

    # User that created the ingredient
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    # Name of the ingredient
    name = models.CharField(max_length=255)

    def __str__(self):
        """Returns the string representation of the ingredient."""
        return self.name


class Tag(models.Model):
    """The Tag model."""

    # User that created the tag
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    # Name of the tag
    name = models.CharField(max_length=255)

    def __str__(self):
        """Returns the string representation of the tag."""
        return self.name
