from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,viewsets
from .models import User, Department
from .serializers import UserSerializer, RegisterUserSerializer, DepartmentSerializer
from django.http import Http404
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)



User = get_user_model()




@extend_schema(tags=['User Management'])
class UserView(APIView):

    @extend_schema(
    tags=['User Management'],
        summary="List Users",
        description="Retrieve a list of users, optionally filtering by department.",
        responses={
            200: UserSerializer(many=True),
            404: {
                "description": "Department not found",
                "content": {
                    "application/json": {
                        "example": {"error": "Department not found"}
                    }
                }
            }
        }
    )
    def get(self, request, format=None):
        department_id = request.query_params.get('department', None)
        
        if department_id:
            try:
                department = Department.objects.get(id=department_id)
                users = User.objects.filter(department=department)
            except Department.DoesNotExist:
                return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    


    @extend_schema(
    tags=['User Management'],
    summary="Create a User",
    description="Create a new user with the provided data.",
    request=RegisterUserSerializer,
    responses={
        201: RegisterUserSerializer,
        400: {
            "description": "Bad Request - Validation failed",
            "content": {
                "application/json": {
                    "example": {"username": ["This field is required."]}
                }
            }
        }
    }
)
    def post(self, request, format=None):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    






@extend_schema(tags=['User Management'])
class UserDetailView(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404


    @extend_schema(
    tags=['User Management'],
    summary="Retrieve a User",
    description="Retrieve a specific user by their ID.",
    responses={
        200: UserSerializer,
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        }
    }
)
    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)




    @extend_schema(
    tags=['User Management'],
    summary="Update a User",
    description="Update a user's information completely by their ID.",
    request=RegisterUserSerializer,
    responses={
        200: RegisterUserSerializer,
        400: {
            "description": "Bad Request - Validation failed",
            "content": {
                "application/json": {
                    "example": {"username": ["This field is required."]}
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        }
    }
)
    def put(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = RegisterUserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    @extend_schema(
    tags=['User Management'],
    summary="Partially Update a User",
    description="Partially update a user's information by their ID.",
    request=RegisterUserSerializer,
    responses={
        200: RegisterUserSerializer,
        400: {
            "description": "Bad Request - Validation failed",
            "content": {
                "application/json": {
                    "example": {"username": ["This field is required."]}
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        }
    }
)
    def patch(self, request, pk, format=None):
        user = self.get_object(pk)
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = RegisterUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(
    tags=['User Management'],
    summary="Delete a User",
    description="Delete a user by their ID.",
    responses={
        204: None,
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        }
    }
)
    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

@extend_schema(tags=['Departments'])
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


    @extend_schema(
        operation_id="list_departments",
        summary="Retrieve a list of departments",
        description="Fetch all departments records in the system.",
        responses={200: DepartmentSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        operation_id="create_department",
        summary="Create a new department",
        description="Create a new department record.",
        request=DepartmentSerializer,
        responses={201: DepartmentSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        operation_id="retrieve_department",
        summary="Retrieve a department",
        description="Fetch a specific department by ID.",
        responses={200: DepartmentSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        operation_id="update_department",
        summary="Update a department",
        description="Update an existing department record.",
        request=DepartmentSerializer,
        responses={200: DepartmentSerializer},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        operation_id="partial_update_department",
        summary="Partially update a department",
        description="Partially update an existing department record.",
        request=DepartmentSerializer,
        responses={200: DepartmentSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        operation_id="destroy_department",
        summary="Delete a department",
        description="Delete an existing department record.",
        responses={204: None},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)



@extend_schema(
    tags=['Token'],
    summary="Validate Microsoft Token",
    description="Validate a Microsoft OAuth token, create or update a user based on the token information, and return JWT tokens.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "token": {
                    "type": "string",
                    "description": "Microsoft OAuth token."
                }
            },
            "required": ["token"],
            "example": {"token": "eyJhbGciOi..."}
        }
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "refresh": {"type": "string", "description": "Refresh token."},
                "access": {"type": "string", "description": "Access token."}
            },
            "example": {
                "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        },
        401: {
            "type": "object",
            "properties": {
                "detail": {"type": "string", "example": "Invalid token"}
            }
        }
    }
)
class MicrosoftTokenValidationView(APIView):
    def post(self, request):
        token = request.data.get('token')

        # Validate token with Microsoft Graph API
        response = requests.get(
            'https://graph.microsoft.com/v1.0/me',
            headers={'Authorization': f'Bearer {token}'}
        )

        if response.status_code != 200:
            return Response({'detail': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

        data = response.json()
        email = data.get('mail') or data.get('userPrincipalName')

        user, created = User.objects.get_or_create(email=email, defaults={
            'first_name': data.get('givenName', ''),
            'last_name': data.get('surname', '')
        })

        if not created:
            user.first_name = data.get('givenName', user.first_name)
            user.last_name = data.get('surname', user.last_name)
            user.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    



@extend_schema_view(
    post=extend_schema(
        summary="Obtain JWT Token Pair",
        description="Obtain a new access and refresh token pair using valid user credentials.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "refresh": {"type": "string", "description": "Refresh token."},
                    "access": {"type": "string", "description": "Access token."}
                },
                "example": {
                    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                }
            },
            401: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "example": "No active account found with the given credentials"}
                }
            }
        },
        tags=['Token']
    )
)
class CustomTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema_view(
    post=extend_schema(
        summary="Refresh JWT Token",
        description="Refresh an existing access token using a refresh token.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {"type": "string", "description": "New access token."}
                },
                "example": {
                    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                }
            },
            401: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "example": "Token is invalid or expired"}
                }
            }
        },
        tags=['Token']
    )
)
class CustomTokenRefreshView(TokenRefreshView):
    pass
