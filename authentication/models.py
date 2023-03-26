"""Authentication models"""
from enum import IntEnum

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class Role(models.Model):
    """Represents user roles (user, moderator, admin)"""

    name = models.CharField(max_length=45)
    title = models.CharField(max_length=45)

    def __str__(self):
        return f"Role {self.pk}: {self.name} ({self.title})"


class Roles(IntEnum):
    """Default roles provided by fixtures/roles.json"""

    USER = 1
    MODERATOR = 2
    ADMIN = 3


class UserManager(BaseUserManager):
    def create_user(self, username, email, password):
        if username is None:
            raise TypeError("Username is required")
        if email is None:
            raise TypeError("Email is required")
        if password is None:
            raise TypeError("Password is required")

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.role = Role.objects.get(pk=Roles.USER)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.role = Role.objects.get(pk=Roles.ADMIN)
        user.save()

        return user


class User(AbstractBaseUser):
    """A user"""
    email = models.EmailField(db_index=True, max_length=255, unique=True)
    username = models.CharField(db_index=True, max_length=255, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    blocked_until = models.DateTimeField(blank=True, null=True, default=None)
    role = models.ForeignKey(Role, default=Roles.USER, on_delete=models.PROTECT)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "password"]

    objects = UserManager()

    @property
    def has_perm(self):
        return lambda _: self.is_superuser

    @property
    def has_module_perms(self):
        return lambda _: self.is_superuser

    @property
    def is_staff(self):
        return self.is_superuser

    @property
    def is_superuser(self):
        return self.role == Role.objects.get(pk=Roles.ADMIN)

    @property
    def is_moderator(self):
        return self.role == Role.objects.get(pk=Roles.MODERATOR)

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def __str__(self):
        return f"{self.id}: {self.email} ({self.username})"
