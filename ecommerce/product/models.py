from django.db import models
from django.conf import settings

class Category(models.TextChoices):
    ELECTRONICS = 'Electronics'
    FASHION = 'Fashion'
    HOME = 'Home'
    BEAUTY = 'Beauty'
    SPORTS = 'Sports' 
    TOYS = 'Toys'
    BOOKS = 'Books'
    OTHER = 'Other'


class Product(models.Model):
    name = models.CharField(max_length=255,blank=False)
    description = models.TextField(max_length=1000,default="", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.CharField(max_length=255,blank=False)
    category = models.CharField(max_length=40,blank=False, choices=Category.choices)
    ratings = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

