from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from model_bakery import baker
from core.models import Recipe, Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicIngredientAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITest(TestCase):
    def setUp(self):
        self.user = baker.make(get_user_model())
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        Ingredient.objects.create(user=self.user, name='sugar')
        Ingredient.objects.create(user=self.user, name='salt')

        ingredients = Ingredient.objects.filter(user=self.user)
        serializer = IngredientSerializer(ingredients, many=True)

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        baker.make(Ingredient)
        ingredient = Ingredient.objects.create(
            user=self.user, name='pineapple')

        ingredients = Ingredient.objects.filter(user=self.user)
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(ingredients.count(), 1)
        self.assertEqual(ingredients[0].name, ingredient.name)

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_ingredient(self):
        ingredient = Ingredient.objects.create(user=self.user, name='sugar')
        payload = {'name': 'vanilla'}

        res = self.client.patch(detail_url(ingredient.id), payload)

        ingredient.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredient.name, payload['name'])

    def test_filter_ingredient_assign_to_recipe(self):
        i1 = Ingredient.objects.create(user=self.user, name='pasta')
        i2 = Ingredient.objects.create(user=self.user, name='apple')
        r1 = Recipe.objects.create(
            user=self.user,
            title='pasta with cheese',
            time_minute=3,
            price=Decimal('44'),
            description='hello with you',
            link='http://test.com/rrecipe.pdf')
        r1.ingredient.add(i1)

        res = self.client.get(INGREDIENTS_URL, {'assign_only': 1})

        s1 = IngredientSerializer(i1)
        s2 = IngredientSerializer(i2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filterd_ingredients_unique(self):
        i1 = Ingredient.objects.create(user=self.user, name='cheese')
        Ingredient.objects.create(user=self.user, name='dfdf')
        r1 = Recipe.objects.create(
            user=self.user,
            title='pasta with cheese',
            time_minute=3, price=Decimal('44'),
            description='hello with you',
            link='http://test.com/rrecipe.pdf'
        )
        r2 = Recipe.objects.create(
            user=self.user, title='21 with cheese',
            time_minute=3,
            price=Decimal(
                '44'),
            description='hello with you',
            link='http://test.com/rrecipe.pdf'
        )

        r1.ingredient.add(i1)
        r2.ingredient.add(i1)

        res = self.client.get(INGREDIENTS_URL, {'assign_only': 1})

        self.assertEqual(len(res.data), 1)
