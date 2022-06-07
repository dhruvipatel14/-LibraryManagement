from enum import Enum

from django.db import models


# Create your models here.

class Roles(Enum):
    ADMIN = "ADMIN"
    USER = "USER"

    @classmethod
    def choices(cls):
        return [(role.value, role.name) for role in cls]


class Users(models.Model):
    class Meta:
        db_table = 'users'

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    password = models.TextField()
    role = models.CharField(choices=Roles.choices(), max_length=20)
