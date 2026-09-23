from django.urls import path
from .views import register,get_user

urlpatterns = [
    path('register/', register,name='register'),
     path('user/', get_user,name='user'),
]