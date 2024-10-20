
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from personnel.views import RegisterUserView



urlpatterns = [
    path('personnel/register/', RegisterUserView.as_view(), name='register'),
    path('personnel/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    #path('personnel/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),




]
