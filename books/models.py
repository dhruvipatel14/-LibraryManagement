from django.db import models


# Create your models here.

class Books(models.Model):
    class Meta:
        db_table = "books"

    name = models.CharField(max_length=255)
    author = models.CharField(max_length=50, null=True)
    publication = models.CharField(max_length=255, null=True)
    no_of_copies = models.IntegerField(default=0)

