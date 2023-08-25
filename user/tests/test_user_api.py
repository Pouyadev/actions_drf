from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    user = get_user_model().objects.create_user(**params)
    return user


class PublicUserApiTest(TestCase):
    def SetUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        payload = {
            'email': 'test@example.com',
            'password': 'test123'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exiat_error(self):
        payload = {
            'email': 'test@example.com',
            'password': 'test123'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_passowrd_too_short_error(self):
        payload = {
            'email': 'test@example.com',
            'password': 'test'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(
            email=payload['email']).exists()
        self.assertFalse(user_exist)

    def test_create_token_for_user(self):
        user_details = {
            'email': 'test@example.com',
            'password': 'test123'
        }
        create_user(**user_details)
        res = self.client.post(TOKEN_URL, user_details)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_tooken_bad_credential_error(self):
        create_user(email='test@example.com', password='test123')
        payload = {
            'email': 'test1@examle.com',
            'password': 'test321'
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_with_blank_password_error(self):
        user_details = {
            'email': 'test@example.com',
            'password': 'test123'
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': ''
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_retrive_user_unauthorized(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='test123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_profile_success(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'email': self.user.email})

    def test_me_post_method_not_allowed(self):
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_update_profile(self):
        payload = {'password':'test1233'}
        res = self.client.patch(ME_URL, payload)
        # self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload['password']))
