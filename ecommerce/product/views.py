from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from utils.responses import api_response
from .models import Category, Product, ProductImage, Review
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductDetailSerializer,
    ProductImageSerializer,
    ReviewSerializer
)
from .filters import ProductFilter
from .permissions import IsAdminOrSellerOrReadOnly, IsReviewOwnerOrReadOnly
from .utils import StandardPagination


@extend_schema_view(
    list=extend_schema(summary="List all root categories with children"),
    retrieve=extend_schema(summary="Get category details"),
    create=extend_schema(summary="Create a category (Admin/Seller)"),
    update=extend_schema(summary="Update a category (Admin/Seller)"),
    destroy=extend_schema(summary="Delete a category (Admin)")
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(parent__isnull=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrSellerOrReadOnly]
    lookup_field = 'id'


@extend_schema_view(
    list=extend_schema(summary="List all active products with pagination & filtering"),
    retrieve=extend_schema(summary="Get product details with images & reviews"),
    create=extend_schema(summary="Create a new product (Admin/Seller)"),
    update=extend_schema(summary="Update product details"),
    destroy=extend_schema(summary="Delete product")
)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'reviews')
    permission_classes = [IsAdminOrSellerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = StandardPagination
    search_fields = ['name', 'description', 'brand']
    ordering_fields = ['price', 'created_at', 'ratings_avg']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(summary="Upload images to product gallery")
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser], permission_classes=[IsAdminOrSellerOrReadOnly])
    def upload_images(self, request, pk=None):
        product = self.get_object()
        files = request.FILES.getlist('images')

        if not files:
            return api_response(
                success=False,
                message="No image files provided.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        created_images = []
        for file in files:
            img = ProductImage.objects.create(product=product, image=file)
            created_images.append(ProductImageSerializer(img).data)

        return api_response(
            success=True,
            message=f"Uploaded {len(created_images)} image(s) successfully.",
            data=created_images,
            status_code=status.HTTP_201_CREATED
        )


@extend_schema_view(
    list=extend_schema(summary="List reviews"),
    create=extend_schema(summary="Add product review"),
    update=extend_schema(summary="Update review"),
    destroy=extend_schema(summary="Delete review")
)
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user', 'product')
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewOwnerOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def perform_create(self, serializer):
        product_id = self.request.data.get('product')
        if Review.objects.filter(product_id=product_id, user=self.request.user).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("You have already submitted a review for this product.")
        serializer.save(user=self.request.user)
