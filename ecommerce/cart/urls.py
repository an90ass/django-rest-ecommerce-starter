from django.urls import path
from .views import CartView, CartItemDetailView, WishlistView, WishlistToggleView

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart_detail'),
    path('cart/items/<int:pk>/', CartItemDetailView.as_view(), name='cart_item_detail'),
    path('wishlist/', WishlistView.as_view(), name='wishlist_detail'),
    path('wishlist/toggle/', WishlistToggleView.as_view(), name='wishlist_toggle'),
]
