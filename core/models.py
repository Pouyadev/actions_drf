from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.text import slugify
from uuid import uuid4
import os


def recipe_image_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{slugify(instance.title)}_{uuid4()}.{ext}'

    return os.path.join('uploads', 'recipe', filename)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, ):
        if not email:
            raise ValueError('email address is required')
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(
            email=self.normalize_email(email), password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=50)
    is_staff = models.BooleanField(default=False)
    data_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'


class Tag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.ManyToManyField(Tag)
    ingredient = models.ManyToManyField(Ingredient)
    title = models.CharField(max_length=50)
    time_minute = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(max_length=500)
    link = models.URLField(max_length=200)
    image = models.ImageField(upload_to=recipe_image_file_path, null=True, blank=True)

    def __str__(self):
        return self.title
