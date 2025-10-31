from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from uuid import uuid4


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        self.first_name = self.username.title()
        super().save(*args, **kwargs)

class Aluno(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    telefone = models.CharField(max_length=14)

    def __str__(self):
        return self.user.username
    

