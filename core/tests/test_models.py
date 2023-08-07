from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    def setUp(self) -> None:
        self.email = 'test@example.com'
        self.password = 'test123'
        return super().setUp()


    def test_create_user_with_email_successful(self):
        user = get_user_model().objects.create_user(
            email=self.email,
            password=self.password
        )
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))

    def test_user_email_normalized(self):
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['TEST2@EXAMPLE.com', 'TEST2@example.com'],
            ['test3@EXAMPLE.COM', 'test3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for entered_email, excepted_email in sample_emails:
            user = get_user_model().objects.create_usser(email=entered_email, password=self.password)
            self.assertEqual(user.email, excepted_email)

         

