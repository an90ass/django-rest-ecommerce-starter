from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .utils import get_paginated_response

from .filters import ProductFilter
from .models import Product
from .serializers import ProductSerializer
from rest_framework.pagination import PageNumberPagination



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
