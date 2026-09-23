from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
from .serializers import SignupSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
# Create your views here.

@api_view(['POST'])
def register(request):
    data = request.data
    serializer = SignupSerializer(data=data)
    if serializer.is_valid():
        user = User.objects.filter(email=data['email']).exists()
        if  user:
            return Response ({"status": "error", "data": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        User.objects.create(
            first_name=data['first_name'], 
            last_name=data['last_name'],

            username=data['email'],
            email=data['email'],
            password=make_password(data['password']))
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
    return Response({"status": "error", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    user = request.user
    serializer = UserSerializer(user, many=False)
    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)