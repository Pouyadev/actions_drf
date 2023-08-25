from decimal import Decimal
from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core import mail
from core import models
from model_bakery import baker


def create_user(email='test@gmail.com', password='test123'):
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    def setUp(self):
        self.email = 'test@example.com'
        self.password = 'test123'

    def test_create_user_with_email_successful(self):
        user = get_user_model().objects.create_user(
            email=self.email,
            password=self.password
        )
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))

    def test_new_user_email_normalized(self):
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['TEST2@EXAMPLE.com', 'TEST2@example.com'],
            ['test3@EXAMPLE.COM', 'test3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for entered_email, excepted_email in sample_emails:
            user = get_user_model().objects.create_user(
                email=entered_email, password=self.password)
            self.assertEqual(user.email, excepted_email)

    def test_new_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email='', password=self.password)

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(
            email=self.email, password=self.password)

        self.assertTrue(user.is_superuser)

    def test_send_email_success(self):
        with self.settings(
                EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
        ):
            mail.send_mail(
                subject='Test subject is here',
                message='Test message is here',
                from_email='testmail@gmail.com',
                recipient_list=['testmail@gmail.com'],
                fail_silently=False,
            )
            self.assertEqual(len(mail.outbox), 1)

    def test_create_recipe(self):
        recipe = baker.make(models.Recipe)
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='Sample Ingredient'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid4')
    def test_recipe_file_name_uuid(self, patched_uuid):
        recipe = baker.make(models.Recipe)
        recipe.title = 'recipe-title'
        recipe.save()

        uuid = 'sample-uuid'
        patched_uuid.return_value = uuid

        file_path = models.recipe_image_file_path(recipe, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{recipe.title}_{uuid}.jpg')
