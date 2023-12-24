"""
Unit Test Suite for the Ingredients API
"""
from core.models import Ingredient
from recipe.serializers import IngredientSerializer

from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model as user_model

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(email='TestEmail@test.com', password='TestPassword'):
    """Create a test user and return it"""
    return user_model().objects.create_user(email, password)


def ingredient_detail_url(ingredient_id):
    """Returns the URL for an ingredient detail"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicIngredientsApiTests(TestCase):
    """Test the publicly available Ingredients API"""

    def setUp(self):
        """Setup the test client"""
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving ingredients"""

        # Attempt to retrieve ingredients without logging in
        res = self.client.get(INGREDIENTS_URL)

        # Check that the response status code is 401 (Unauthorized)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test private Ingredients API"""

    def setUp(self):
        """Setup the test client"""
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_get_ingredients_list(self):
        """Test getting ingredients list"""

        # Create sample ingredients
        Ingredient.objects.create(user=self.user, name='Rosemary')
        Ingredient.objects.create(user=self.user, name='Thyme')

        # Retrieve ingredients (GET request)
        res = self.client.get(INGREDIENTS_URL)

        # Retrieve ingredients from the database (alphabetical order)
        ingredients = Ingredient.objects.all().order_by('-name')

        # Serialize the ingredients
        serializer = IngredientSerializer(ingredients, many=True)

        # Check that the response status code is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check that the response data matches the serialized data
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test only ingredients for the authenticated user are returned"""

        # Create sample ingredient for the authenticated user
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Feta Cheese'
        )

        # Create a second user
        usr_2 = create_user(email='TestEmail2@test.com')

        # Create sample ingredient for the second user
        Ingredient.objects.create(user=usr_2, name='Creme Fraiche')

        # Retrieve ingredients (GET request)
        res = self.client.get(INGREDIENTS_URL)

        # Check that the response status code is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check that only one ingredient is returned
        self.assertEqual(len(res.data), 1)

        # Check that the returned ingredient is the correct one
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_update_ingredient_successful(self):
        """Test updating an ingredient is successful"""

        # Create a sample ingredient
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Flour'
        )

        # Create the payload to update the ingredient
        payload = {
            'name': 'Mashed Potato'
        }

        # Update the ingredient (PUT request)
        res = self.client.patch(
            ingredient_detail_url(ingredient.id),
            payload
        )

        # Refresh the ingredient from the database
        ingredient.refresh_from_db()

        # Check that the response status code is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check that the ingredient was updated
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient_successful(self):
        """Test deleting an ingredient is successful"""

        # Create a sample ingredient
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Tomato'
        )

        # Delete the ingredient (DELETE request)
        res = self.client.delete(ingredient_detail_url(ingredient.id))

        # Check that the response status code is 204 (No Content)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        # Check that the ingredient was deleted
        self.assertEqual(Ingredient.objects.count(), 0)
