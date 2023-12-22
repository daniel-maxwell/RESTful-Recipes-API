"""
Django Models Unit Test Suite for the core app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model as user_model
from decimal import Decimal
from core import models

def create_user(email="TestEmail@test.com", password="TestPassword"):
    """Create a test user and return it"""
    return user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test Django Models"""

    def test_create_user_with_email_was_successful(self):
        """Test create user with email is successful"""

        email = 'email@test.com'  # Valid dummy email
        pw = 'testpassword1234'  # Valid dummy password

        # Create a user with dummy email and password
        usr = user_model().objects.create_user(
            email=email,
            password=pw,
        )

        self.assertEqual(usr.email, email)  # Check if email is correct
        self.assertTrue(usr.check_password(pw))  # Check if password is correct

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""

        # Samples check that the domain is lowercased (as per the email spec)
        sample_emails = [
            ['testemail1@TEST.COM', 'testemail1@test.com'],
            ['TestEmail2@Test.com', 'TestEmail2@test.com'],
        ]

        # Iterate though sample emails, check that each email is normalized
        for testEmail, expectedEmail in sample_emails:
            usr = user_model().objects.create_user(testEmail, 'test1234')
            self.assertEqual(usr.email, expectedEmail)

    def test_new_user_missing_email_raises_error(self):
        """Test creating user with no email raises an error"""

        # Ensure that creating a user with no email raises a ValueError
        with self.assertRaises(ValueError):
            user_model().objects.create_user('', 'password1234')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        usr = user_model().objects.create_superuser(
            'testemail@test.com',
            'password1234'
        )
        self.assertTrue(usr.is_superuser)
        self.assertTrue(usr.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe"""

        # Create a user
        user=user_model().objects.create_user(
            'TestEmail@Test.com',
            'TestPassword'
        )

        # Create a recipe
        recipe=models.Recipe.objects.create(
            user=user,
            title='Test Recipe',
            time_minutes=5,
            price=Decimal('10.00'),
            description='Test Description'
        )

        # Check that the recipe was created
        self.assertEqual(str(recipe), recipe.title)
