from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from parts.models import Parts, PartsInventory
from planes.models import Planes, PlanesInventory
from personnel.models import CustomUser
from .models import AssemblyHistory
from django.db import models

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# PLANE ASSEMBLY TEAM CRUD VIEWS
class PlaneManufacturingView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Attempts to manufacture a plane based on the specified `plane_id`. The user must be part of the 'Assembly Team' to perform this operation.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'plane_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the plane to be manufactured'),
            },
            required=['plane_id'],
        ),
        responses={
            200: openapi.Response(
                description="Successfully manufactured the plane.",
            ),
            400: openapi.Response(
                description="Bad request. Possible reasons include missing `plane_id`, parsing errors, or insufficient parts.",
                examples={
                    "application/json": {
                        "status": False,
                        "error": "plane_id is required."
                    }
                }
            ),
            403: openapi.Response(
                description="Forbidden. The user is not authorized to manufacture planes.",
            ),
            404: openapi.Response(
                description="Plane not found.",
            )
        }
    )

    def post(self, request):
        user = request.user
        plane_id = request.data.get('plane_id')

        # Validate the plane_id
        if not plane_id:
            return Response({'status': False, 'error': 'plane_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user is in the 'Assembly Team'
        if user.department is None or user.department.name != 'Assembly Team':
            return Response({'status': False, 'error': 'User is not part of the Assembly Team.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if the plane exists
        try:
            plane = Planes.objects.get(id=plane_id)
        except Planes.DoesNotExist:
            return Response({'status': False, 'error': 'Plane not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Parse the required parts
        try:
            required_parts = eval(plane.required_parts)  # Assuming required_parts is a string like "(1, 2, 3, 4)"
        except Exception as e:
            return Response({'status': False, 'error': 'Failed to parse required parts.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if all required parts are available in the inventory for the specified plane
        insufficient_parts = []
        for part_id in required_parts:
            # Get all inventory records for the specified part and plane
            parts_inventories = PartsInventory.objects.filter(part_id=part_id, plane_id=plane_id)

            # Sum the inventory across all records for the specified plane
            total_inventory = sum(p.inventory for p in parts_inventories)

            if total_inventory < 1:
                insufficient_parts.append(part_id)

        if insufficient_parts:
            # Retrieve the names of the insufficient parts
            part_names = [Parts.objects.get(id=part_id).name for part_id in insufficient_parts]
            # Construct the error message
            error_message = f"There is no {', '.join(part_names)} to create {plane.name}."
            return Response({
                'status': False,
                'error': error_message
            }, status=status.HTTP_400_BAD_REQUEST)

        # Decrement inventory for all required parts for the specified plane
        used_parts = []
        for part_id in required_parts:
            # Get all inventory records for the specified part and plane and decrement one by one
            parts_inventories = PartsInventory.objects.filter(part_id=part_id, plane_id=plane_id)

            for parts_inventory in parts_inventories:
                if parts_inventory.inventory > 0:
                    parts_inventory.inventory -= 1
                    parts_inventory.save()
                    used_parts.append(part_id)
                    break  # Stop once we've decremented the inventory for this part

        # Increment the plane's inventory
        plane_inventory, created = PlanesInventory.objects.get_or_create(plane=plane, defaults={'inventory': 0})
        plane_inventory.inventory += 1
        plane_inventory.save()

        # Record the assembly history
        AssemblyHistory.objects.create(
            used_parts=str(used_parts),
            plane=plane
        )

        # Construct the response
        data = {
            'status': True,
            'message': f"Successfully manufactured a '{plane.name}'",
            'plane_id': plane_id,
            'new_inventory': plane_inventory.inventory,
            'used_parts': used_parts
        }

        return Response(data, status=status.HTTP_200_OK)

class PlaneManufacturerInfoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Returns a list of all planes and their inventory for users who are part of the 'Assembly Team'.",
        responses={
            200: openapi.Response(
                description="Successfully retrieved the plane inventory.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Request success status'),
                        'department_name': openapi.Schema(type=openapi.TYPE_STRING,
                                                          description='Name of the user\'s department'),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'plane_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                               description='ID of the plane'),
                                    'plane_name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                 description='Name of the plane'),
                                    'plane_inventory': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                      description='Current inventory of the plane'),
                                }
                            ),
                            description='List of planes with their inventory'
                        )
                    }
                )
            ),
            403: openapi.Response(
                description="Forbidden. The user is not part of the Assembly Team.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Request success status'),
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        },
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="JWT Authorization header. Format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )


    def get(self, request):
        user = request.user

        # Check if the user's department is "Assembly Team"
        if user.department is None or user.department.name != 'Assembly Team':
            return Response({'status': False, 'error': 'User is not part of the Assembly Team.'}, status=status.HTTP_403_FORBIDDEN)

        # Fetch all planes and their inventory
        planes = PlanesInventory.objects.all()

        # Prepare the response data
        data = []
        for plane_inventory in planes:
            plane_data = {
                'plane_id': plane_inventory.plane.id,
                'plane_name': plane_inventory.plane.name,
                'plane_inventory': plane_inventory.inventory
            }
            data.append(plane_data)

        # Construct the final response
        response_data = {
            'status': True,
            'department_name': user.department.name,
            'data': data
        }

        return Response(response_data, status=status.HTTP_200_OK)

class PlaneManufacturerRecycle(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Recycles one unit of the specified plane from the inventory for users who are part of the 'Assembly Team'.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'plane_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the plane to recycle'),
            },
            required=['plane_id'],
        ),
        responses={
            200: openapi.Response(
                description="Successfully recycled one unit of the plane.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Request success status'),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                        'new_inventory': openapi.Schema(type=openapi.TYPE_INTEGER, description='Updated inventory count for the plane'),
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request. The plane_id is missing, or there is no plane to recycle.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Request success status'),
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            ),
            403: openapi.Response(
                description="Forbidden. The user is not part of the Assembly Team.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Request success status'),
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            ),
            404: openapi.Response(
                description="Not found. The plane does not exist in the database or inventory.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Request success status'),
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        },
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="JWT Authorization header. Format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )

    def delete(self, request):
        user = request.user
        plane_id = request.data.get('plane_id')

        # Validate the input parameter
        if not plane_id:
            return Response({'status': False, 'error': 'plane_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user is in the "Assembly Team" department
        if user.department is None or user.department.name != 'Assembly Team':
            return Response({'status': False, 'error': 'User is not part of the Assembly Team.'}, status=status.HTTP_403_FORBIDDEN)

        # Get the plane name from the Planes model
        try:
            plane = Planes.objects.get(id=plane_id)
            plane_name = plane.name
        except Planes.DoesNotExist:
            return Response({'status': False, 'error': f'Plane with ID {plane_id} does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the plane exists in the inventory
        try:
            plane_inventory = PlanesInventory.objects.get(plane_id=plane_id)
        except PlanesInventory.DoesNotExist:
            return Response({'status': False, 'error': f'{plane_name} not found in inventory.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if there is any inventory to recycle
        if plane_inventory.inventory <= 0:
            return Response({'status': False, 'error': f'No {plane_name} to recycle.'}, status=status.HTTP_400_BAD_REQUEST)

        # Decrement the inventory
        plane_inventory.inventory -= 1
        plane_inventory.save(update_fields=['inventory'])

        # Return a success response
        response_data = {
            'status': True,
            'message': f"Successfully recycled one {plane_name}.",
            'new_inventory': plane_inventory.inventory
        }

        return Response(response_data, status=status.HTTP_200_OK)


# PART MANUFACTURER TEAM CRUD VIEWS
class PartManufacturingView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


    @swagger_auto_schema(
        operation_description="Manufactures a specified part for a given plane. Increases the inventory count for the part associated with the plane.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'plane_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the plane'),
                'part_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the part to manufacture'),
            },
            required=['plane_id', 'part_id'],
        ),
        responses={
            200: openapi.Response(
                description="Successfully manufactured the part.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, description='Operation status'),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                        'plane_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the plane'),
                        'part_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the part'),
                        'new_inventory': openapi.Schema(type=openapi.TYPE_INTEGER, description='Updated inventory count for the part'),
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request due to missing or invalid parameters.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            ),
            401: openapi.Response(
                description="Unauthorized. Authentication token is missing or invalid.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            ),
            403: openapi.Response(
                description="Forbidden. User does not have access to manufacture the part.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            ),
            404: openapi.Response(
                description="Not found. The plane or part does not exist.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        },
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="JWT Authorization header. Format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )

    def post(self, request):
        user = request.user
        plane_id = request.data.get('plane_id')
        part_id = request.data.get('part_id')

        # Validate required fields
        if not plane_id:
            return Response({'error': 'plane_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not part_id:
            return Response({'error': 'part_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.auth:
            return Response({'error': 'Authentication token is required.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the part exists
        try:
            part = Parts.objects.get(id=part_id)
        except Parts.DoesNotExist:
            return Response({'error': 'Part not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the plane exists
        try:
            plane = Planes.objects.get(id=plane_id)
        except Planes.DoesNotExist:
            return Response({'error': 'Plane not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has access to the part (based on department)
        if user.department is None or user.department.id != part.department.id:
            return Response({'error': 'User does not have access to this part.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if a PartsInventory record exists for the given plane and part
        parts_inventory, created = PartsInventory.objects.get_or_create(
            plane_id=plane_id,
            part_id=part_id
        )

        if created:
            # If a new record is created, set the inventory to 1
            parts_inventory.inventory = 1
            parts_inventory.save()
        else:
            # If the record already exists, increment the inventory
            parts_inventory.inventory += 1
            parts_inventory.save()

        # Construct the response
        data = {
            'status': 'success',
            'message': f"Successfully manufactured a '{part.name}' for '{plane.name}'",
            'plane_id': plane_id,
            'part_id': part_id,
            'new_inventory': parts_inventory.inventory
        }

        return Response(data, status=status.HTTP_200_OK)

class PartManufacturerInfoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieves information about parts related to the user's department, including the total inventory of relevant parts for each plane. The user must not be in the 'Assembly Team' and must belong to a valid department.",
        responses={
            200: openapi.Response(
                description="Successfully retrieved part manufacturer information.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Request success status'),
                        'department_name': openapi.Schema(type=openapi.TYPE_STRING,
                                                          description='Name of the user\'s department'),
                        'part_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                  description='Part ID related to the department', nullable=True),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'plane_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                               description='ID of the plane'),
                                    'plane_name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                 description='Name of the plane'),
                                    'part_count': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                 description='Total inventory count of relevant parts'),
                                }
                            ),
                            description='List of planes with relevant part inventory details'
                        )
                    }
                )
            ),
            403: openapi.Response(
                description="Forbidden. The user is either in the 'Assembly Team' or has no valid department.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Request success status'),
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        },
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="JWT Authorization header. Format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )

    def get(self, request):
        user = request.user

        # Check if the user is not in the Assembly Team and their department is not None or 0
        if user.department is None or user.department.name == 'Assembly Team':
            return Response({'status': False, 'error': 'User is either in the Assembly Team or has no valid department.'}, status=status.HTTP_403_FORBIDDEN)

        department_name = user.department.name
        department_id = user.department.id

        # Fetch the part_id for the user's department
        try:
            department_part = Parts.objects.filter(department_id=department_id).first()
            part_id = department_part.id if department_part else None
        except Parts.DoesNotExist:
            part_id = None

        # Fetch all planes
        planes = Planes.objects.all()

        # Prepare the response data
        data = []
        for plane in planes:
            # Parse the required parts for the plane
            try:
                required_parts = eval(plane.required_parts)  # Assuming required_parts is a string like "(1, 2, 3, 4)"
            except Exception:
                continue  # Skip if there's an error in parsing

            # Filter the parts that belong to the user's department
            department_parts = Parts.objects.filter(id__in=required_parts, department=user.department)

            # Sum the inventory for the matching parts in PartsInventory
            part_inventory_total = PartsInventory.objects.filter(part__in=department_parts, plane=plane).aggregate(total_inventory=models.Sum('inventory'))['total_inventory']

            if part_inventory_total and part_inventory_total > 0:
                # Add plane info to the response
                data.append({
                    'plane_id': plane.id,
                    'plane_name': plane.name,
                    'part_count': part_inventory_total
                })

        # Construct the final response, including the part_id found for the department
        response_data = {
            'status': True,
            'department_name': department_name,
            'part_id': part_id,
            'data': data
        }

        return Response(response_data, status=status.HTTP_200_OK)


class PartManufacturerRecycleView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Recycles one unit of the specified part for a given plane. Decreases the inventory count for the part associated with the plane. The user must have permission to recycle the part.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'plane_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the plane'),
                'part_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the part to recycle'),
            },
            required=['plane_id', 'part_id'],
        ),
        responses={
            200: openapi.Response(
                description="Successfully recycled the part.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Operation success status'),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                        'plane_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the plane'),
                        'part_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the part'),
                        'new_inventory': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                        description='Updated inventory count for the part'),
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request due to missing parameters or no inventory to recycle.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Operation success status'),
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            ),
            403: openapi.Response(
                description="Forbidden. User does not have permission to recycle the part.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Operation success status'),
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            ),
            404: openapi.Response(
                description="Not found. The specified part is not in the inventory for the given plane.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Operation success status'),
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        },
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="JWT Authorization header. Format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )

    def delete(self, request):
        user = request.user
        plane_id = request.data.get('plane_id')
        part_id = request.data.get('part_id')

        # Validate the input parameters
        if not plane_id:
            return Response({'status': False, 'error': 'plane_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not part_id:
            return Response({'status': False, 'error': 'part_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the PartsInventory entry exists for the given plane and part
        try:
            parts_inventory = PartsInventory.objects.get(plane_id=plane_id, part_id=part_id)
        except PartsInventory.DoesNotExist:
            return Response({'status': False, 'error': 'Part not found in inventory for the specified plane.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user's department matches the part's department
        if user.department is None or user.department.id != parts_inventory.part.department.id:
            return Response({'status': False, 'error': 'User does not have permission to recycle this part.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if there is any inventory to recycle
        if parts_inventory.inventory <= 0:
            return Response({'status': False, 'error': 'There is no part you can recycle.'}, status=status.HTTP_400_BAD_REQUEST)

        # Decrement the inventory
        parts_inventory.inventory -= 1
        parts_inventory.save()

        # Get part and plane names for the success message
        part_name = parts_inventory.part.name
        plane_name = parts_inventory.plane.name

        # Return a success response
        response_data = {
            'status': True,
            'message': f"Successfully recycled one {part_name} for {plane_name}.",
            'plane_id': plane_id,
            'part_id': part_id,
            'new_inventory': parts_inventory.inventory
        }

        return Response(response_data, status=status.HTTP_200_OK)

class AssembleHistoryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieves the assembly history for users who are part of the 'Assembly Team'. The history includes details about planes and the parts used in the assembly.",
        responses={
            200: openapi.Response(
                description="Successfully retrieved the assembly history.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Operation success status'),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'plane_name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                 description='Name of the plane'),
                                    'used_parts': openapi.Schema(type=openapi.TYPE_STRING,
                                                                 description='Names of the parts used in the assembly, separated by commas'),
                                    'date': openapi.Schema(type=openapi.FORMAT_DATETIME,
                                                           description='Date of the assembly')
                                }
                            ),
                            description='List of assembly history records'
                        )
                    }
                )
            ),
            403: openapi.Response(
                description="Forbidden. The user is not part of the Assembly Team.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Operation success status'),
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        },
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="JWT Authorization header. Format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )

    def get(self, request):
        user = request.user

        # Check if the user's department is "Assembly Team"
        if user.department.name != 'Assembly Team':
            return Response({'status': False, 'error': 'User is not part of the Assembly Team.'}, status=status.HTTP_403_FORBIDDEN)

        # Fetch the assembly history
        assembly_history = AssemblyHistory.objects.all()

        # Prepare the response data
        data = []
        for history in assembly_history:
            # Parse the used_parts field assuming it's stored as a string representation of a list (e.g., "[1, 2, 3]")
            try:
                used_part_ids = eval(history.used_parts)
                # Fetch the part names based on the part IDs
                part_names = Parts.objects.filter(id__in=used_part_ids).values_list('name', flat=True)
                part_names_list = list(part_names)
            except Exception:
                part_names_list = []

            # Add each entry to the response data
            data.append({
                'plane_name': history.plane.name,
                'used_parts': ', '.join(part_names_list),
                'date': history.date
            })

        # Construct the final response
        response_data = {
            'status': True,
            'data': data
        }

        return Response(response_data, status=status.HTTP_200_OK)


