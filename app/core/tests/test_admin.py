"""
Tests for Django admin modifications
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model as user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Tests Django Admin Site"""

    def setUp(self):
        """Set up test client and create users"""
        # Create test client
        self.client = Client()

        # Create admin user
        self.admin_user = user_model().objects.create_superuser(
            email = 'admin@test.com',
            password = 'testpassword1234'
        )
        # Log in admin user
        self.client.force_login(self.admin_user)

        # Create a regular user
        self.user = user_model().objects.create_user(
            email = 'user@test.com',
            password = 'testpassword1234',
            name = 'Test User'
        )


    def test_create_user_page(self):
        """Test that the create user page functions correctly"""

        # Generate URL for create user page
        url = reverse('admin:core_user_add')

        # Use test client to perform HTTP GET on URL
        res = self.client.get(url)

        # Check that the HTTP response is OK (200)
        self.assertEqual(res.status_code, 200)


    def test_users_list(self):
        """Test that users are listed on user page"""

        # Generate URL for user list
        url = reverse('admin:core_user_changelist')

        # Use test client to perform HTTP GET on URL
        res = self.client.get(url)

        # Check that response contains regular user
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)


    def test_edit_user_page(self):
        """Test that the edit user page functions correctly"""

        # Generate URL for edit user page
        url = reverse('admin:core_user_change', args=[self.user.id])

        # Use test client to perform HTTP GET on URL
        res = self.client.get(url)

        # Check that the HTTP response is OK (200)
        self.assertEqual(res.status_code, 200)
        