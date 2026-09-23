from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from utils.responses import api_response
from .serializers import (
    UserRegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer
)


from rest_framework.throttling import ScopedRateThrottle

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    @extend_schema(
        tags=['Authentication'],
        summary="Register a new user",
        description="Creates a new user account (Customer, Seller, or Admin) and returns user profile.",
        responses={201: UserSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return api_response(
            success=True,
            message="User account created successfully.",
            data=UserSerializer(user).data,
            status_code=status.HTTP_201_CREATED
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    @extend_schema(
        summary="User Login (JWT Token)",
        description="Authenticate user with email & password and return JWT access/refresh tokens alongside user metadata."
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return api_response(
                success=True,
                message="Authentication successful.",
                data=response.data,
                status_code=status.HTTP_200_OK
            )
        return response


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get current user profile",
        responses={200: UserSerializer}
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return api_response(
            success=True,
            message="Profile retrieved successfully.",
            data=serializer.data
        )

    @extend_schema(
        summary="Update current user profile",
        request=UserUpdateSerializer,
        responses={200: UserSerializer}
    )
    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(
            success=True,
            message="Profile updated successfully.",
            data=UserSerializer(request.user).data
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Change user password",
        request=ChangePasswordSerializer
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return api_response(
            success=True,
            message="Password updated successfully."
        )