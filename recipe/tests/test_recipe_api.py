from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status
from model_bakery import baker
from core.models import Ingredient, Recipe, Tag
from recipe.serializers import RecipeLinkSerializer, RecipeSerializer, RecipeDetailSerializer
from PIL import Image
import tempfile
import os

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    default = {
        'title': 'Sample recipe title',
        'time_minute': 22,
        'price': Decimal('5.25'),
        'description': 'Sample recipe description',
        'link': 'http://example.com/recipe.pdf'
    }
    default.update(**params)

    recipe = Recipe.objects.create(user=user, **default)
    return recipe


class PublicRecipeAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()


    def test_auth_required(self):
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com', password='test123')
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.factory = APIRequestFactory()


    def test_retrive_recipes(self):
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeLinkSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_recipe_list_limited_to_user(self):
        other_user = get_user_model().objects.create_user(
            email='test2@example.com',
            password='tfst123'
        )
        create_recipe(user=self.user)
        create_recipe(user=other_user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeLinkSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_get_recipe_detail(self):
        recipe = create_recipe(user=self.user)

        res = self.client.get(detail_url(recipe.id))
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)


    def test_create_recipe(self):
        payload = {
            'title': 'Sample title',
            'description': 'Sample description',
            'time_minute': 4,
            'price': Decimal('5.5'),
            'link': 'http://test.com/recipe.pdf'
        }

        res = self.client.post(RECIPES_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipe.user, self.user)
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)


    def test_create_recipe_with_new_tags(self):
        payload = {
            'title': 'simple title',
            'description': 'sample description',
            'time_minute': 6,
            'price': Decimal('5.8'),
            'link': 'http://test.com/recipe.pdf',
            'tag': [{'name': 'first'}, {'name': 'second'}]
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tag.count(), 2)
        for tag in payload['tag']:
            exists = recipe.tag.filter(
                user=self.user, name=tag['name']).exists()
            self.assertTrue(exists)


    def test_create_recipe_with_existing_tag(self):
        created_tag = Tag.objects.create(user=self.user, name='orange')
        payload = {
            'title': 'simple title',
            'description': 'sample description',
            'time_minute': 6,
            'price': Decimal('5.8'),
            'link': 'http://test.com/recipe.pdf',
            'tag': [{'name': 'orange'}, {'name': 'kiwi'}]
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.tag.count(), 2)
        self.assertIn(created_tag, recipe.tag.all())

        for tag in payload['tag']:
            exists = recipe.tag.filter(
                user=self.user, name=tag['name']).exists()
            self.assertTrue(exists)


    def test_create_tag_on_update(self):
        recipe = create_recipe(user=self.user)
        payload = {'tag': [{'name': 'first'}]}

        res = self.client.patch(detail_url(recipe.id), payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_tag = Tag.objects.get(user=self.user, name='first')
        self.assertIn(new_tag, recipe.tag.all())


    def test_update_tag_assign_tag(self):
        tag = Tag.objects.create(user=self.user, name='first')
        recipe = create_recipe(user=self.user)
        recipe.tag.add(tag)

        second_tag = Tag.objects.create(user=self.user, name='second')
        payload = {'tag': [{'name': 'second'}]}

        res = self.client.patch(detail_url(recipe.id), payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tag.count(), 1)
        self.assertIn(second_tag, recipe.tag.all())


    def test_clear_recipe_tags(self):
        tag = Tag.objects.create(user=self.user, name='first')
        recipe = create_recipe(user=self.user)
        recipe.tag.add(tag)

        payload = {'tag': []}

        res = self.client.patch(detail_url(recipe.id), payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tag.count(), 0)


    def test_filter_by_tags(self):
        r1 = create_recipe(user=self.user, title='chiken')
        t1 = Tag.objects.create(user=self.user, name='xx')
        r1.tag.add(t1)
        r2 = create_recipe(user=self.user, title='apple cake')
        t2 = Tag.objects.create(user=self.user, name='xxx')
        r2.tag.add(t2)
        r3 = create_recipe(user=self.user, title='fish and chinps')

        request = self.factory.get(RECIPES_URL)

        s1 = RecipeLinkSerializer(r1, context={'request': request})
        s2 = RecipeLinkSerializer(r2, context={'request': request})
        s3 = RecipeLinkSerializer(r3, context={'request': request})

        query_params = {'tags': f'{t1.id},{t2.id}'}
        res = self.client.get(RECIPES_URL, query_params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)


    def test_filter_by_ingredients(self):
        r1 = create_recipe(user=self.user, title='chiken pizza')
        i1 = Ingredient.objects.create(user=self.user, name='cheese')
        r1.ingredient.add(i1)
        r2 = create_recipe(user=self.user, title='apple cake')
        i2 = Ingredient.objects.create(user=self.user, name='apple')
        r2.ingredient.add(i2)

        r3 = create_recipe(user=self.user, title='fish chinps')

        request = self.factory.get(RECIPES_URL)

        query_params = {'ingredients': f'{i1.id},{i2.id}'}
        res = self.client.get(RECIPES_URL, query_params)

        s1 = RecipeLinkSerializer(r1, context={'request': request})
        s2 = RecipeLinkSerializer(r2, context={'request': request})
        s3 = RecipeLinkSerializer(r3, context={'request': request})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)


class ImageUploadTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com', password='test123')
        self.recipe = create_recipe(user=self.user)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def tearDown(self):
        self.recipe.image.delete()

    # def test_upload_image_bad_request(self):
    #     payload = {'image': 'not an image'}
    #     res = self.client.post(detail_url(self.recipe.id),
    #                            payload)

    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_image(self):
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new(mode='RGB', size=(10, 10))
            img.save(fp=image_file, format='JPEG')
            image_file.seek(0)

            payload = {'image': image_file}
            res = self.client.post(detail_url(
                self.recipe.id), payload, 'multipart')

        self.recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))
