from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AddressViewSet, CheckoutView, OrderViewSet

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('', include(router.urls)),
]
