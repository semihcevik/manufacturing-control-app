from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from personnel.models import CustomUser
from .models import Departments

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class DepartmentInfoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Returns the user's department information. If the user belongs to the 'Assembly Team', access permissions will be adjusted accordingly.",
        responses={
            201: openapi.Response(
                description="Successful response",
            ),
            404: openapi.Response(description="Department information not found.")
        },
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Bearer JWT token. Authentication token for the logged-in user.",
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )
    def get(self, request):
        user = request.user

        # If department is None, return an appropriate response
        if not user.department:
            data = {
                'error': 'Department ID is null or blank.'
            }
            return Response(data, status=status.HTTP_201_CREATED)

        # If department exists, construct the response
        department_name = user.department.name
        user_department_id = user.department.id
        is_assembly_team = department_name == 'Assembly Team'

        # Retrieve all departments and construct the departments list, excluding "Assembly Team"
        departments_data = []
        all_departments = Departments.objects.all()

        for dept in all_departments:
            # Skip the "Assembly Team" department
            if dept.name == 'Assembly Team':
                continue

            # Set isAccess to True only if the department matches the user's department
            # If the user is in the Assembly Team, then isAccess should only be True for "Assembly Team"
            is_access = dept.id == user_department_id if not is_assembly_team else dept.name == 'Assembly Team'
            departments_data.append({
                'department_name': dept.name,
                'department_id': dept.id,
                'isAccess': is_access
            })

        # Construct the response
        data = {
            'isAssemblyTeam': is_assembly_team,
            'username': user.username,
            'departments': departments_data
        }

        return Response(data, status=status.HTTP_201_CREATED)



