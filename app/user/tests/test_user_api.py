"""
Test suite for the User API
"""

from django.contrib.auth import get_user_model as user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


CREATE_USER_URL = reverse('user:create')  # URL for creating a user
TOKEN_URL = reverse('user:token')  # URL for creating a token
ME_URL = reverse('user:me')  # URL for getting the current user

def create_user(**params):
    """Helper function to create a new user"""
    return user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """Test public features of the User API"""

    def setUp(self):
        self.client = APIClient()  # Create a client

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'TestEmail@test.com',
            'password': 'TestPassword',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        # Check that the response is 201 (User created)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Get the user from the database
        user = user_model().objects.get(email=payload['email'])

        # Check that the password is correct
        self.assertTrue(user.check_password(payload['password']))

        # Check that the password is not returned in the response
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test creating a user that already exists returns an error"""
        payload = {
            'email': 'TestEmail@test.com',
            'password': 'TestPassword',
            'name': 'Test Name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        # Check that the response is 400 (Bad Request)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_with_short_password_error(self):
        """Test creating a user with a password less than 8 characters returns an error"""
        payload = {
            'email': 'TestEmail@test.com',
            'password': 'pw',
            'name': 'Test Name'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        # Check that the response is 400 (Bad Request)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that the user was not created
        user_exists = user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_user_token_creation(self):
        """Test that a token is created for a user that supplies valid credentials"""
        user_details = {
            'name': 'Test Name',
            'email': 'TestEmail@test.com',
            'password': 'TestPassword123',
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }

        res = self.client.post(TOKEN_URL, payload)

        # Check that the response is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check that the token is in the response
        self.assertIn('token', res.data)


    def test_user_token_invalid_credentials(self):
        """Test that a token is not created for a user that supplies invalid credentials"""
        create_user(email='TestEmail@Test.com', password='TestPassword123')

        # Create and send payload with an invalid password
        payload = {'email': 'TestEmail@test.com', 'password': 'InvalidPassword'}
        res = self.client.post(TOKEN_URL, payload)

        # Check that the response is 400 (Bad Request)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that the token is not in the response
        self.assertNotIn('token', res.data)

    def test_create_token_blank_password(self):
        """Test that an error is raised when the user does not supply a password"""
        payload = {'email': 'TestEmail@Test.com', 'password': ''}

        res = self.client.post(TOKEN_URL, payload)

        # Check that the response is 400 (Bad Request)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that the token is not in the response
        self.assertNotIn('token', res.data)

    def retrieve_unauthorized_user(self):
        """Test that authentication is required to retrieve a user"""
        res = self.client.get(ME_URL)

        # Check that the response is 401 (Unauthorized)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    """Test private features of the User API"""

    def setUp(self):
        self.user = create_user(
            email = 'TestEmail@test.com',
            password = 'TestPassword123',
            name = 'Test Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_success(self):
        """Test that a user can retrieve their own profile"""
        res = self.client.get(ME_URL)

        # Check that the response is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check that the response contains the correct data
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_request_to_me_not_allowed(self):
        """Test that POST is not allowed on the me URL"""
        res = self.client.post(ME_URL, {})

        # Check that the response is 405 (Method Not Allowed)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test that a user can update their own profile if they're authenticated"""
        payload = {'name': 'New Name', 'password': 'NewPassword123'}

        res = self.client.patch(ME_URL, payload)

        # Check that the response is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check that the user model has been updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))