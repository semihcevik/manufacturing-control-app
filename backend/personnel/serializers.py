from rest_framework import serializers
from .models import CustomUser
from departments.models import Departments

class CustomUserSerializer(serializers.ModelSerializer):
    # Use PrimaryKeyRelatedField to handle the department as an ID
    department = serializers.PrimaryKeyRelatedField(queryset=Departments.objects.all(), required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'department', 'password')  # Include the fields that exist in the model
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Extract the department ID from validated_data, if provided
        department_id = validated_data.pop('department', None)

        # Create the user instance
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Set the department if department_id is provided
        if department_id:
            user.department_id = department_id
            user.save()

        return user
