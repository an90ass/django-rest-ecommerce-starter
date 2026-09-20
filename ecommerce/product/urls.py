from django.urls import path
from .views import get_all_products

urlpatterns = [
    path('products/', get_all_products,name='products'),
]