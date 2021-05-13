from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from users.managers import UserManager


class User(AbstractUser):
    """
        Custom user model for authentication instead of usernames.
    """
    username = None
    email = models.EmailField(_('email address'), max_length=30, db_index=True, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    phone = models.CharField(max_length=13, blank=True)

    def __str__(self):
        return self.email
