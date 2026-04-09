from django.db import models

class sector(models.Model):
    name = models.CharField(max_length=100)
    acronym = models.CharField(max_length=10)
    
    def __str__(self):
        return self.name


class users(models.Model):
    name = models.CharField(max_length=100)
    user_function = models.CharField(max_length=100)

    sector = models.ForeignKey(sector, on_delete=models.CASCADE)


    def __str__(self):
        return self.name
    
# Create your models here.
