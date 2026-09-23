from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404

from utils.responses import api_response
from product.models import Product
from .models import Cart, CartItem, Wishlist, WishlistItem
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    AddCartItemSerializer,
    UpdateCartItemSerializer,
    WishlistSerializer,
    WishlistItemSerializer
)


def _get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.headers.get('X-Session-ID') or request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_id=session_id)
    return cart


class CartView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="Get current shopping cart", responses={200: CartSerializer})
    def get(self, request):
        cart = _get_or_create_cart(request)
        serializer = CartSerializer(cart)
        return api_response(
            success=True,
            message="Cart retrieved successfully.",
            data=serializer.data
        )

    @extend_schema(summary="Add item to shopping cart", request=AddCartItemSerializer, responses={200: CartSerializer})
    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = _get_or_create_cart(request)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                return api_response(
                    success=False,
                    message=f"Insufficient stock. Only {product.stock} items available.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            if quantity > product.stock:
                cart_item.delete()
                return api_response(
                    success=False,
                    message=f"Insufficient stock. Only {product.stock} items available.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        return api_response(
            success=True,
            message="Item added to cart successfully.",
            data=CartSerializer(cart).data
        )

    @extend_schema(summary="Clear shopping cart")
    def delete(self, request):
        cart = _get_or_create_cart(request)
        cart.items.all().delete()
        return api_response(
            success=True,
            message="Cart cleared successfully.",
            data=CartSerializer(cart).data
        )


class CartItemDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="Update cart item quantity", request=UpdateCartItemSerializer)
    def patch(self, request, pk):
        cart = _get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=pk, cart=cart)

        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_quantity = serializer.validated_data['quantity']

        if new_quantity > cart_item.product.stock:
            return api_response(
                success=False,
                message=f"Insufficient stock. Only {cart_item.product.stock} items available.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = new_quantity
        cart_item.save()

        return api_response(
            success=True,
            message="Cart item updated successfully.",
            data=CartSerializer(cart).data
        )

    @extend_schema(summary="Remove item from cart")
    def delete(self, request, pk):
        cart = _get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=pk, cart=cart)
        cart_item.delete()
        return api_response(
            success=True,
            message="Item removed from cart.",
            data=CartSerializer(cart).data
        )


class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get user wishlist", responses={200: WishlistSerializer})
    def get(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        return api_response(
            success=True,
            message="Wishlist retrieved successfully.",
            data=WishlistSerializer(wishlist).data
        )


class WishlistToggleView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Toggle item in user wishlist")
    def post(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return api_response(
                success=False,
                message="product_id is required.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        product = get_object_or_404(Product, id=product_id, is_active=True)
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

        item = WishlistItem.objects.filter(wishlist=wishlist, product=product).first()
        if item:
            item.delete()
            added = False
            msg = "Product removed from wishlist."
        else:
            WishlistItem.objects.create(wishlist=wishlist, product=product)
            added = True
            msg = "Product added to wishlist."

        return api_response(
            success=True,
            message=msg,
            data={"added": added, "wishlist": WishlistSerializer(wishlist).data}
        )
