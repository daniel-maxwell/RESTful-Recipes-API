"""
Unit Test Suite for the Recipe APIs.
"""
from core.models import Recipe, Tag
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model as user_model
from django.core.serializers.json import DjangoJSONEncoder

from rest_framework import status
from rest_framework.test import APIClient

import json
from decimal import Decimal

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return the URL for a recipe detail"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def create_test_recipe(**params):
    """Create a test recipe and return it"""

    # Define default recipe parameters
    defaults = {
        'title': 'Test Recipe',
        'time_minutes': 10,
        'price': Decimal('15.10'),
        'description': 'Test Description',
        'link': 'http://www.test.com/recipe.pdf'
    }

    # Update defaults with any passed parameters
    defaults.update(params)

    # Create and return the recipe
    recipe = Recipe.objects.create(**defaults)
    return recipe

def create_test_tag(user, name='Test Tag'):
    """Create a test tag and return it"""
    return Tag.objects.create(user=user, name=name)

def create_user(**params):
    """Create a test user and return it"""
    return user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
    """Test the publicly available Recipe API features"""

    def setUp(self):
        """Set up the test client"""
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to call the API"""

        # Use test client to perform HTTP GET on the Recipes URL
        res = self.client.get(RECIPES_URL)

        # Check that the response is 401 (Unauthorized)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test the private Recipe API features"""

    def setUp(self):
        """Set up the test client and create a user"""
        self.client = APIClient()

        # Create a user
        self.user = user_model().objects.create_user(
            'TestEmail@test.com',
            'TestPassword'
        )
        # Log the user in
        self.client.force_authenticate(self.user)

    def test_create_dummy_recipe(self):
        """Test creating a dummy recipe"""

        # Define a recipe payload
        payload = {
            'title': 'Test Recipe',
            'time_minutes': 15,
            'price': str(Decimal('15.10')),
            'description': 'Test Description',
            'link': 'http://www.test.com/recipe.pdf',
            'tags': [{'name': 'Test Tag'}]  # Add this line
        }

        # Encode payload as JSON and POST to the Recipes URL
        res = self.client.post(
            RECIPES_URL,
            json.dumps(payload),
            content_type='application/json'
        )

        # Check the response is 201 (Created)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Retrieve the recipe from the database
        recipe = Recipe.objects.get(id=res.data['id'])

        # Check the recipe was created with the correct values
        for key in payload.keys() - {'tags'}:
            self.assertEqual(str(getattr(recipe, key)), str(payload[key]))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with existing tags"""
        # Define recipe payload with tags
        payload = {
            'title': 'Test Title',
            'tags': [
                {'name': 'Test Tag 1'},
                {'name': 'Test Tag 2'},
            ],
            'time_minutes': 60,
            'description': 'Test Description',
            'price': 20.00
        }

        # Encode payload as JSON and POST to the Recipes URL
        res = self.client.post(
            RECIPES_URL,
            json.dumps(payload, cls=DjangoJSONEncoder),
            content_type='application/json'
        )

        # Check the response is 201 (Created)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Retrieve the recipe from the database
        recipe = Recipe.objects.get(id=res.data['id'])

        # Retrieve the tags associated with the recipe
        tags = recipe.tags.all()

        # Check the recipe has the correct number of tags
        self.assertEqual(tags.count(), 2)

        # Check the recipe has the correct tags
        tag_names = [tag.name for tag in tags]
        self.assertIn('Test Tag 1', tag_names)
        self.assertIn('Test Tag 2', tag_names)

    def test_get_recipe_details(self):
        """Test retrieving recipe details"""

        # Create a recipe
        recipe = create_test_recipe(user=self.user)

        # Generate the URL for the recipe detail
        url = detail_url(recipe.id)

        # Use test client to perform HTTP GET on the recipe detail URL
        res = self.client.get(url)

        # Pass the recipe to the serializer
        serializer = RecipeDetailSerializer(recipe)

        # Check the response is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check the response data matches the serialized data
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_list(self):
        """Test retrieving a list of recipes"""

        # Create some recipes
        create_test_recipe(user=self.user)
        create_test_recipe(user=self.user)

        # Use test client to perform HTTP GET on the Recipes URL
        res = self.client.get(RECIPES_URL)

        # Retrieve all recipes from database (ordered by recency)
        recipes = Recipe.objects.all().order_by('-id')

        # Pass the recipes to the serializer
        serializer = RecipeSerializer(recipes, many=True)

        # Check the response is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check the response data matches the serialized data
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_list_limited_to_user(self):
        """Test recipe list is limited to authenticated user"""

        # Create a second user
        new_user = user_model().objects.create_user(
            'newTestUsr@Test.com',
            'newTestPassword',
        )

        # Create some recipes for each user
        create_test_recipe(user=new_user)
        create_test_recipe(user=self.user)

        # Use test client to perform HTTP GET on the Recipes URL
        res = self.client.get(RECIPES_URL)

        # Retrieve all recipes for the authenticated user
        recipes = Recipe.objects.filter(user=self.user)

        # Pass the recipes to the serializer
        serializer = RecipeSerializer(recipes, many=True)

        # Check the response is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check the response data matches the serialized data
        self.assertEqual(res.data, serializer.data)

    def test_partial_update_recipe(self):
        """Test partially updating a recipe (PATCH)"""
        original_url = 'http://www.test.com/recipe.pdf'

        # Create a recipe from the original URL
        recipe = create_test_recipe(
            user=self.user,
            title='Test Recipe Title',
            link=original_url
        )

        # Define the new recipe payload
        payload = {'title': 'New Test Recipe Title'}

        # Generate the URL for the recipe detail
        url = detail_url(recipe.id)

        # Perform HTTP PATCH on the recipe detail URL
        res = self.client.patch(url, payload)

        # Check the response is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Refresh the recipe from the database
        recipe.refresh_from_db()

        # Check the recipe was updated with the new title
        self.assertEqual(recipe.title, payload['title'])

        # Check the recipe was NOT updated with a new link
        self.assertEqual(recipe.link, original_url)

        # Check the recipe was NOT updated with a new user
        self.assertEqual(recipe.user, self.user)

    def test_complete_update_recipe(self):
        """Test completely updating a recipe (PUT)"""

        # Create a recipe
        recipe = create_test_recipe(
            user=self.user,
            title='Test Recipe Title',
            time_minutes=20,
            price=Decimal('20.20'),
            description='Test Description',
            link='http://www.test.com/recipe.pdf'
        )

        # Define the new recipe payload
        payload = {
            'title': 'New Test Recipe Title',
            'time_minutes': 10,
            'price': Decimal('10.00'),
            'description': 'New Test Description',
            'link': 'http://www.newtest.com/recipe.pdf'
        }

        # Generate the URL for the recipe detail
        url = detail_url(recipe.id)

        # Perform HTTP PUT on the recipe detail URL
        res = self.client.put(url, payload)

        # Check the response is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Refresh the recipe from the database
        recipe.refresh_from_db()

        # Check the recipe was updated with the new values
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)

        # Check the recipe was NOT updated with a new user
        self.assertEqual(recipe.user, self.user)

    def test_create_tag_when_updating_recipe(self):
        """Test tag creation when recipes are updated"""
        # Create a recipe
        recipe = create_test_recipe(user=self.user)

        # Create a tag
        tag = create_test_tag(user=self.user, name='Test Tag')

        # Generate the URL for the recipe detail
        url = detail_url(recipe.id)

        # Define the recipe update payload
        payload = {'tags': [{'name': 'Test Tag'}]}

        # Perform HTTP PATCH on the recipe detail URL
        res = self.client.patch(
            url,
            json.dumps(payload, cls=DjangoJSONEncoder),
            content_type='application/json'
        )

        # Check the response is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # GET the tag from the database
        new_tag = Tag.objects.get(name='Test Tag')

        # Check the tag was created and is associated with the recipe
        self.assertTrue(new_tag in recipe.tags.all())

    def test_assign_tag_when_updating_recipe(self):
        """Test assignment of an existing tag when recipes are updated"""

        # Create a test tag
        old_tag = create_test_tag(user=self.user, name='Old Test Tag')

        # Create a test recipe
        recipe = create_test_recipe(user=self.user)

        # Assign the test tag to the test recipe
        recipe.tags.add(old_tag)

        # Generate the URL for the recipe detail
        url = detail_url(recipe.id)

        # Define the recipe update payload (with new tag)
        payload = {'tags': [{'name': 'New Test Tag'}]}

        # Perform HTTP PATCH on the recipe detail URL
        res = self.client.patch(
            url,
            json.dumps(payload, cls=DjangoJSONEncoder),
            content_type='application/json'
        )

        # Check the response is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Refresh the recipe to get updated data
        recipe.refresh_from_db()

        # Check the old tag is no longer associated with the recipe
        self.assertNotIn(old_tag, recipe.tags.all())

        # Check the new tag is associated with the recipe
        tag_names = [tag.name for tag in recipe.tags.all()]
        self.assertIn('New Test Tag', tag_names)

    def test_update_recipe_delete_tags(self):
        """Test deleting assigned tags from a recipe"""

        # Create a recipe
        recipe = create_test_recipe(user=self.user)

        # Create a tag
        tag = create_test_tag(user=self.user, name='Test Tag')

        # Assign the tag to the recipe
        recipe.tags.add(tag)

        # Generate the URL for the recipe detail
        url = detail_url(recipe.id)

        # Define the recipe update payload (no tags)
        payload = {'tags': []}

        # Perform HTTP PATCH, providing updated recipe update payload
        res = self.client.patch(url, payload, format='json')

        # Check the response is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check tags were cleared from the recipe
        self.assertEqual(recipe.tags.count(), 0)

    def test_delete_recipe(self):
        """Test deleting a recipe"""

        # Create a recipe
        recipe = create_test_recipe(user=self.user)

        # Generate the URL for the recipe detail
        url = detail_url(recipe.id)

        # Perform HTTP DELETE on the recipe detail URL
        res = self.client.delete(url)

        # Check the response is 204 (No Content)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        # Check the recipe was deleted
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_error(self):
        """Test deleting another user's recipe returns an error"""

        # Create a second user
        new_user = create_user(
            email='secondUser@test.com',
            password='secondUserPassword'
        )

        # Create a recipe for the second user
        recipe = create_test_recipe(user=new_user)

        # Generate the URL for the recipe detail
        url = detail_url(recipe.id)

        # Perform HTTP DELETE on the recipe detail URL
        res = self.client.delete(url)

        # Check the response is 404 (Not Found)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        # Check the recipe was NOT deleted
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
