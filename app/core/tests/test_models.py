"""
Unit Test Suite for Django Models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model as user_model


class ModelTests(TestCase):
    """Test Django Models"""

    def test_create_user_with_email_was_successful(self):
        """Test create user with email is successful"""

        email = 'email@test.com'    # Valid dummy email
        pw = 'testpassword1234'     # Valid dummy password

        # Create a user with dummy email and password
        usr = user_model().objects.create_user(
            email=email,
            password=pw,
        )

        self.assertEqual(usr.email, email)      # Check if email is correct
        self.assertTrue(usr.check_password(pw))     # Check if password is correct

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""

        # Samples check that the domain is lowercased (as per the email spec)
        sample_emails = [
            ['testemail1@TEST.COM', 'testemail1@test.com'],
            ['TestEmail2@Test.com', 'TestEmail2@test.com'],
        ]

        for testEmail, expectedEmail in sample_emails:
            usr = user_model().objects.create_user(testEmail, 'test1234')
            self.assertEqual(usr.email, expectedEmail)
