"""
Unit Test Suite for the Recipe APIs.
"""
from core.models import Recipe, Ingredient, Tag
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


def recipe_detail_url(recipe_id):
    """Returns the URL for a recipe detail"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


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
            'tags': [{'name': 'Test Tag'}]
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

    def create_dummy_recipe_and_new_ingredients(self):
        """Test creating a dummy recipe with ingredients"""

        # Define a recipe payload
        payload = {
            'title': 'Test Recipe',
            'time_minutes': 15,
            'price': 5.00,
            'ingredients': [
                {'name': 'Test Ingredient 1'},
                {'name': 'Test Ingredient 2'}
            ],
            'description': 'Test Description',
            'link': 'http://www.test.com/recipe.pdf',
        }

        # Encode payload as JSON and POST to the Recipes URL
        res = self.client.post(
            RECIPES_URL,
            json.dumps(payload),
            content_type='application/json'
        )

        # Check the response is 201 (Created)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Retrieve all recipes associated with the user
        recipes = Recipe.objects.filter(user=self.user)

        # Check there is only one recipe associated with the user
        self.assertEqual(recipes.count(), 1)

        # Get the recipe that was created
        recipe = recipes[0]

        # Check the recipe has the correct number of ingredients
        self.assertEqual(recipe.ingredients.count(), 2)

        # Check the recipe has the correct ingredients
        for ingredient in payload['ingredients']:
            self.assertTrue(
                Ingredient.objects.filter(
                    user=self.user,
                    name=ingredient['name']
                ).exists()
            )

    def test_create_dummy_recipe_with_existing_ingredients(self):
        """Test creating a dummy recipe with existing ingredients"""

        # Define a recipe payload
        payload = {
            'title': 'Test Recipe',
            'time_minutes': 15,
            'price': 5.00,
            'ingredients': [
                {'name': 'Test Ingredient 1'},
                {'name': 'Test Ingredient 2'}
            ],
            'description': 'Test Description',
            'link': 'http://www.test.com/recipe.pdf',
        }

        # Encode payload as JSON and POST to the Recipes URL
        res = self.client.post(
            RECIPES_URL,
            json.dumps(payload),
            content_type='application/json'
        )

        # Check the response is 201 (Created)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Retrieve all recipes associated with the user
        recipes = Recipe.objects.filter(user=self.user)

        # Check there is only one recipe associated with the user
        self.assertEqual(recipes.count(), 1)

        # Get the recipe that was created
        recipe = recipes[0]

        # Check the recipe has the correct number of ingredients
        self.assertEqual(recipe.ingredients.count(), 2)

        # Retrieve the ingredients associated with the recipe
        ingredients = recipe.ingredients.all()

        # Check the recipe has the correct ingredients
        ingredient_names = [ingredient.name for ingredient in ingredients]
        self.assertIn('Test Ingredient 1', ingredient_names)
        self.assertIn('Test Ingredient 2', ingredient_names)

    def test_create_dummy_recipe_and_new_tags(self):
        """Test creating a recipe with new tags"""

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

    def test_create_dummy_recipe_with_existing_tags(self):
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
        url = recipe_detail_url(recipe.id)

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

    def test_filter_recipes_by_ingredients(self):
        recipe_1 = create_test_recipe(user=self.user, title="Pea Soup")
        recipe_2 = create_test_recipe(user=self.user, title="Brushetta")
        recipe_3 = create_test_recipe(user=self.user, title="Lasagna")

        ingredient_1 = Ingredient.objects.create(
            user=self.user,
            name='Peas'
        )
        ingredient_2 = Ingredient.objects.create(
            user=self.user,
            name='Tomatoes'
        )

        recipe_1.ingredients.add(ingredient_1)
        recipe_2.ingredients.add(ingredient_2)

        params = {'ingredients': f'{ingredient_1.id},{ingredient_2.id}'}

        res = self.client.get(RECIPES_URL, params)

        serializer_1 = RecipeSerializer(recipe_1)
        serializer_2 = RecipeSerializer(recipe_2)
        serializer_3 = RecipeSerializer(recipe_3)

        self.assertIn(serializer_1.data, res.data)
        self.assertIn(serializer_2.data, res.data)
        self.assertNotIn(serializer_3.data, res.data)

    def test_filter_recipes_by_tags(self):
        recipe_1 = create_test_recipe(user=self.user, title="Pea Soup")
        recipe_2 = create_test_recipe(user=self.user, title="Brushetta")
        recipe_3 = create_test_recipe(user=self.user, title="Lasagna")

        tag_1 = create_test_tag(user=self.user, name="Vegan")
        tag_2 = create_test_tag(user=self.user, name="Quick and Easy")

        recipe_1.tags.add(tag_1)
        recipe_2.tags.add(tag_2)

        params = {'tags': f'{tag_1.id},{tag_2.id}'}

        res = self.client.get(RECIPES_URL, params)

        serializer_1 = RecipeSerializer(recipe_1)
        serializer_2 = RecipeSerializer(recipe_2)
        serializer_3 = RecipeSerializer(recipe_3)

        self.assertIn(serializer_1.data, res.data)
        self.assertIn(serializer_2.data, res.data)
        self.assertNotIn(serializer_3.data, res.data)

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
        url = recipe_detail_url(recipe.id)

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
        url = recipe_detail_url(recipe.id)

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

    def test_create_ingredient_when_updating_recipe(self):
        """Test ingredient creation when recipes are updated"""

        # Create a recipe
        recipe = create_test_recipe(user=self.user)

        # Define the recipe update payload (with new ingredient)
        payload = {'ingredients': [{'name': 'Test Ingredient'}]}

        # Perform HTTP PATCH on the recipe detail URL
        res = self.client.patch(
            recipe_detail_url(recipe.id),
            json.dumps(payload, cls=DjangoJSONEncoder),
            content_type='application/json'
        )

        # Check the response is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # GET the ingredient from the database
        new_ingredient = Ingredient.objects.get(name='Test Ingredient')

        # Check the ingredient was created and is associated with the recipe
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_assign_ingredient_when_updating_recipe(self):
        """Test assignment of existing ingredient when recipes are updated"""

        # Create a test ingredient
        old_ingredient = Ingredient.objects.create(
            user=self.user,
            name='Old Ingredient'
        )

        # Create a test recipe
        recipe = create_test_recipe(user=self.user)

        # Assign the test ingredient to the test recipe
        recipe.ingredients.add(old_ingredient)

        # Define the recipe update payload (with new ingredient)
        payload = {'ingredients': [{'name': 'New Ingredient'}]}

        # Perform HTTP PATCH on the recipe detail URL
        res = self.client.patch(
            recipe_detail_url(recipe.id),
            json.dumps(payload, cls=DjangoJSONEncoder),
            content_type='application/json'
        )

        # Check the response is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Refresh the recipe to get updated data
        recipe.refresh_from_db()

        # Check the old ingredient is no longer associated with the recipe
        self.assertNotIn(old_ingredient, recipe.ingredients.all())

        # Check the new ingredient is associated with the recipe
        ingredient_names = [ing.name for ing in recipe.ingredients.all()]
        self.assertIn('New Ingredient', ingredient_names)

    def test_update_recipe_delete_ingredients(self):
        """Test deleting assigned ingredients from a recipe"""

        # Create a recipe
        recipe = create_test_recipe(user=self.user)

        # Create an ingredient
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Test Ingredient'
        )

        # Assign the ingredient to the recipe
        recipe.ingredients.add(ingredient)

        # Define the recipe update payload (no ingredients)
        payload = {'ingredients': []}

        # Perform HTTP PATCH, providing updated recipe update payload
        res = self.client.patch(
            recipe_detail_url(recipe.id),
            payload,
            format='json')

        # Check the response is 200 (OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check ingredients were cleared from the recipe
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_create_tag_when_updating_recipe(self):
        """Test tag creation when recipes are updated"""
        # Create a recipe
        recipe = create_test_recipe(user=self.user)

        # Generate the URL for the recipe detail
        url = recipe_detail_url(recipe.id)

        # Define the recipe update payload (with new tag)
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
        url = recipe_detail_url(recipe.id)

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
        url = recipe_detail_url(recipe.id)

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
        url = recipe_detail_url(recipe.id)

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
        url = recipe_detail_url(recipe.id)

        # Perform HTTP DELETE on the recipe detail URL
        res = self.client.delete(url)

        # Check the response is 404 (Not Found)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        # Check the recipe was NOT deleted
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
