from django.urls import path
from .views import get_all_products,get_product_by_id

urlpatterns = [
    path('products/', get_all_products,name='products'),
    path('products/<int:pk>/', get_product_by_id, name='product-detail'),
]