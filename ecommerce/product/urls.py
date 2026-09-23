from django.urls import path
from .views import get_all_products,get_product_by_id,add_new_product

urlpatterns = [
    path('products/', get_all_products,name='products'),
    path('products/<int:pk>/', get_product_by_id, name='product-detail'),
    path('products/new',add_new_product, name='product-create'),

]