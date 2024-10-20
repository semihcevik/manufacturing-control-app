from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from .serializers import CustomUserSerializer
from personnel.models import CustomUser

class RegisterUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = CustomUserSerializer