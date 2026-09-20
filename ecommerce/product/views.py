from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
@api_view(['GET'])
def get_all_products(request):
    products = Product.objects.all()
    if not products:
        return Response({
            "status": "error",
            "message": "No products found"
        }, status=404)
    serializer = ProductSerializer(products, many=True)
    print(serializer.data)
    return Response({
        "status": "success",
        "products": serializer.data

    }, status=200)

