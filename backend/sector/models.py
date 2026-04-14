from django.db import models

class Sector(models.Model):
    name = models.CharField(max_length=100)
    acronym = models.CharField(max_length=10)

    def __str__(self):
        return self.name