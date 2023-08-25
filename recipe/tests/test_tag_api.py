from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Recipe, Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='test@example.com', password='test123'):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITest(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name='first')
        Tag.objects.create(user=self.user, name='second')

        tags = Tag.objects.filter(user=self.user)
        serializer = TagSerializer(tags, many=True)

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_tag_limited_to_user(self):
        other_user = create_user(email='other@gmail.com')
        tag = Tag.objects.create(user=self.user, name='first')
        Tag.objects.create(user=other_user, name='second')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        tag = Tag.objects.create(user=self.user, name='first')

        payload = {'name': 'second'}

        res = self.client.patch(detail_url(tag.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_destroy_tag(self):
        tag = Tag.objects.create(user=self.user, name='first')

        res = self.client.delete(detail_url(tag.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRaises(tag.DoesNotExist)

    def test_filtered_tag_assing_to_recipe(self):
        t1 = Tag.objects.create(user=self.user, name='vegan')
        t2 = Tag.objects.create(user=self.user, name='meat')
        r1 = Recipe.objects.create(
            user=self.user,
            title='pasta with cheese',
            time_minute=3,
            price=Decimal('44'),
            description='hello with you',
            link='http://test.com/rrecipe.pdf'
        )
        r1.tag.add(t1)

        res = self.client.get(TAGS_URL, {'assign_only': 1})

        s1 = TagSerializer(t1)
        s2 = TagSerializer(t2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        t1 = Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=self.user, name='hoo')

        r1 = Recipe.objects.create(
            user=self.user,
            title='pasta with cheese',
            time_minute=3,
            price=Decimal('44'),
            description='hello with you',
            link='http://test.com/rrecipe.pdf'
        )

        r2 = Recipe.objects.create(
            user=self.user,
            title='dd with cheese',
            time_minute=3,
            price=Decimal('31'),
            description='hello with you',
            link='http://test.com/rrecipe.pdf'
        )

        r1.tag.add(t1)
        r2.tag.add(t1)

        res = self.client.get(TAGS_URL, {'assign_only': 1})

        self.assertEqual(len(res.data), 1)



