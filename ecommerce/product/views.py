from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .utils import get_paginated_response

from .filters import ProductFilter
from .models import Product
from .serializers import ProductSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
def get_all_products(request):
    base_queryset = Product.objects.select_related('user').order_by('-created_at')
    filterset = ProductFilter(request.GET, queryset=base_queryset)
    paginated_queryset = get_paginated_response(request, filterset.qs, ProductSerializer)
    print(paginated_queryset)
    total_count = filterset.qs.count()

    return paginated_queryset

@api_view(['GET'])
def get_product_by_id(request, pk):
    product = get_object_or_404(Product, id=pk)
    serializer = ProductSerializer(product, many=False)
    return Response({
        "status": "success",
        "product": serializer.data
    }, status=200)
@api_view(['POST'])
@permission_classes([IsAuthenticated])

def add_new_product(request):
    data = request.data
    serializer = ProductSerializer(data=data, many=False)
    if serializer.is_valid():
        Product.objects.create(
           **data,user=request.user
        )
        response = ProductSerializer(Product.objects.all(), many=False)
        return Response({
            "status": "success",
            "product": response.data
        }, status=200)
    else:
        return Response(
            {
                "status": "error",
                 "product": serializer.errors
                    },
                status=400)

