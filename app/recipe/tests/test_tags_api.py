"""
Unit Test Suite for the Tags API
"""
from core.models import Recipe, Tag
from recipe.serializers import TagSerializer

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model as user_model

from rest_framework import status
from rest_framework.test import APIClient

from decimal import Decimal


TAGS_URL = reverse('recipe:tag-list')


def create_user(email='TestEmail@test.com', password='TestPassword'):
    """Create a test user and return it"""
    return user_model().objects.create_user(email, password)


def tag_detail_url(tag_id):
    """Return the URL for a tag detail"""
    return reverse('recipe:tag-detail', args=[tag_id])


class PublicTagsApiTests(TestCase):
    """Test the publicly available Tags API"""

    def setUp(self):
        """Setup the test client"""
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""

        # Attempt to retrieve tags without logging in
        res = self.client.get(TAGS_URL)

        # Check that the response status code is 401 (Unauthorized)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test private Tags API"""

    def setUp(self):
        """Setup the test client"""
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""

        # Create sample tags
        Tag.objects.create(user=self.user, name='Quick and Easy')
        Tag.objects.create(user=self.user, name='Breakfast')

        # Attempt to get tags
        res = self.client.get(TAGS_URL)

        # Retrieve all tags from the database in descending order
        tags = Tag.objects.all().order_by('-name')

        # Serialize the tags
        serializer = TagSerializer(tags, many=True)

        # Check that the response status code is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check that the response data matches the serialized tags
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""

        # Create a new user
        newUser = create_user(
            email='TestEmail2@test.com',
            password='TestPassword2'
        )

        # Create sample tags
        Tag.objects.create(user=newUser, name='Low Carb')

        # Create sample tags for the authenticated user
        tag = Tag.objects.create(user=self.user, name='Vegetarian')

        # Attempt to get tags
        res = self.client.get(TAGS_URL)

        # Check that the response status code is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check response data only contains a single tag
        self.assertEqual(len(res.data), 1)

        # Check response data contains the authenticated user's tag
        self.assertEqual(res.data[0]['name'], tag.name)

        # Check response data contains the authenticated user's tag id
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_filter_tags_to_only_assigned(self):
        """Test filtering tags to only those assigned to recipes"""

        # Create a test recipe
        new_recipe = Recipe.objects.create(
            user=self.user,
            title='Sushi',
            time_minutes=10,
            price=Decimal('5.00')
        )

        # Create sample tag
        tag_1 = Tag.objects.create(user=self.user, name='Low Carb')

        # Assign tag to the test recipe
        new_recipe.tags.add(tag_1)

        # Attempt to get tag
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        # Check that the response status code is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check that only one tag is returned
        self.assertEqual(len(res.data), 1)

        # Check that the returned tag is the correct one
        self.assertEqual(res.data[0]['name'], tag_1.name)

    def test_filter_tags_no_duplicates(self):
        """Test that filtered tags do not contain duplicates"""

        # Create two test recipes
        test_recipe_1 = Recipe.objects.create(
            user=self.user,
            title='Korean Chicken',
            time_minutes=10,
            price=Decimal('9.00')
        )
        test_recipe_2 = Recipe.objects.create(
            user=self.user,
            title='Pizza',
            time_minutes=15,
            price=Decimal('12.00')
        )

        # Create two tags, saving one to a variable
        tag = Tag.objects.create(user=self.user, name='Quick and Easy')
        Tag.objects.create(user=self.user, name='Vegetarian')

        # Assign first tag to the test recipes
        test_recipe_1.tags.add(tag)
        test_recipe_2.tags.add(tag)

        # Attempt to get tags
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        # Check that the response status code is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check that only one tag is returned
        self.assertEqual(len(res.data), 1)

    def test_update_tag_successful(self):
        """Test updating a tag with a valid payload is successful"""

        # Create a tag
        tag = Tag.objects.create(user=self.user, name='Test Tag')

        # Create a payload
        payload = {'name': 'Updated Tag Name'}

        # Attempt to update the tag
        res = self.client.patch(tag_detail_url(tag.id), payload)

        # Refresh the tag from the database
        tag.refresh_from_db()

        # Check that the response status code is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check that the tag name was updated
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag_successful(self):
        """Test deleting a tag is successful"""

        # Create a tag
        tag = Tag.objects.create(user=self.user, name='Test Tag')

        # Attempt to delete the tag
        res = self.client.delete(tag_detail_url(tag.id))

        # Check that the response status code is 204 (No Content)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        # Check that the tag was deleted
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())
