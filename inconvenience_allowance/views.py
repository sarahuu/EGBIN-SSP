from rest_framework import status, viewsets, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import InconvenienceRequest, InconvenienceRequestLine, Day
from .serializers import InconvenienceRequestSerializer,InconvenienceRequestLineSerializer, DaySerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema(tags=['Days'])
class DayViewSet(viewsets.ModelViewSet):
    queryset = Day.objects.all()
    serializer_class = DaySerializer

    @extend_schema(
        operation_id="list_days",
        summary="Retrieve a list of days",
        description="Fetch all day records in the system.",
        responses={200: DaySerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        operation_id="create_day",
        summary="Create a new day",
        description="Create a new day record.",
        request=DaySerializer,
        responses={201: DaySerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        operation_id="retrieve_day",
        summary="Retrieve a day",
        description="Fetch a specific day by ID.",
        responses={200: DaySerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        operation_id="update_day",
        summary="Update a day",
        description="Update an existing day record.",
        request=DaySerializer,
        responses={200: DaySerializer},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        operation_id="partial_update_day",
        summary="Partially update a day",
        description="Partially update an existing day record.",
        request=DaySerializer,
        responses={200: DaySerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        operation_id="destroy_day",
        summary="Delete a day",
        description="Delete an existing day record.",
        responses={204: None},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    


@extend_schema(tags=['Inconvenience Request'])
class InconvenienceRequestView(APIView):
    permission_classes = [IsAuthenticated]


    @extend_schema(
        operation_id="create_request",
        summary="Create a new request",
        description="Create a new request record.",
        request=InconvenienceRequestSerializer,
        responses={201: InconvenienceRequestSerializer},
    )
    def post(self, request):
        data = request.data
        serializer = InconvenienceRequestSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    @extend_schema(
        operation_id="List Inconvenience Request",
        summary="List Inconvenience Request",
        description="List all Inconvenience Requests",
        responses={
            200: InconvenienceRequestSerializer(many=True),
            404: "Not Found",
        }
    )
    def get(self, request):
        inconvenience_requests = InconvenienceRequest.objects.all()
        serializer = InconvenienceRequestSerializer(inconvenience_requests, many=True)
        return Response(serializer.data)



@extend_schema(tags=['Inconvenience Request'])
class InconvenienceRequestDetailView(APIView):
    permission_classes = [IsAuthenticated]
    

    @extend_schema(
        operation_id="Retrieve Inconvenience Request",
        summary="Retrieve Inconvenience Request",
        description="Retrieve a specific Inconvenience Request by its ID, or list all Inconvenience Requests if no ID is provided.",
        responses={
            200: InconvenienceRequestSerializer(many=True),
            404: "Not Found",
        }
    )
    def get(self, request, pk):
        inconvenience_request = get_object_or_404(InconvenienceRequest, pk=pk)
        serializer = InconvenienceRequestSerializer(inconvenience_request)
        return Response(serializer.data)


    @extend_schema(
        operation_id="Update Inconvenience Request",
        summary="Update Inconvenience Request",
        description="Update an existing Inconvenience Request by its ID.",
        request=InconvenienceRequestSerializer,
        responses={
            200: InconvenienceRequestSerializer,
            400: "Bad Request - ID is required for updating or validation failed",
            404: "Not Found - Inconvenience Request not found with the provided ID",
        }
    )
    def put(self, request, pk=None):
        if not pk:
            return Response({"detail": "ID is required for updating"}, status=status.HTTP_400_BAD_REQUEST)
        
        inconvenience_request = get_object_or_404(InconvenienceRequest, pk=pk)
        serializer = InconvenienceRequestSerializer(inconvenience_request, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(
        operation_id="Delete Inconvenience Request",
        summary="Delete Inconvenience Request",
        description="Delete an existing Inconvenience Request by its ID.",
        responses={
            204: "No Content - The Inconvenience Request was successfully deleted.",
            400: "Bad Request - ID is required for deletion",
            404: "Not Found - Inconvenience Request not found with the provided ID",
        }
    )
    def delete(self, request, pk=None):
        if not pk:
            return Response({"detail": "ID is required for deletion"}, status=status.HTTP_400_BAD_REQUEST)
        
        inconvenience_request = get_object_or_404(InconvenienceRequest, pk=pk)
        inconvenience_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)











@extend_schema(tags=['Inconvenience Request Lines'])
class InconvenienceRequestLineView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="List_Inconvenience_Request_Line",
        summary="List Inconvenience Request Line",
        description="List all Inconvenience Request Lines",
        responses={
            200: InconvenienceRequestLineSerializer(many=True),
            404: {
                "application/json": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "User not found"}
                    }
                }
            }

        }
    )
    def get(self, request):
        inconvenience_request_lines = InconvenienceRequestLine.objects.all()
        serializer = InconvenienceRequestLineSerializer(inconvenience_request_lines, many=True)
        return Response(serializer.data)



@extend_schema(tags=['Inconvenience Request Lines'])
class InconvenienceRequestLineDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['inconvenience_request_id'] = self.kwargs.get('pk')
        return context

    @extend_schema(
        operation_id="Create Inconvenience Request Line",
        summary="Create Inconvenience Request Line",
        description="Create a new Inconvenience Request Line linked to a specific Inconvenience Request.",
        request=InconvenienceRequestLineSerializer,
        responses={
            201: InconvenienceRequestLineSerializer,
            400: "Bad Request - Validation failed",
            404: "Not Found - Inconvenience Request not found with the provided ID",
        }
    )
    def post(self, request, pk):
        try:
            inconvenience_request = InconvenienceRequest.objects.get(id=pk)
        except InconvenienceRequest.DoesNotExist:
            return Response({'detail': 'Inconvenience Request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        data['inconvenience_request'] = inconvenience_request.id  # Link to the inconvenience request

        serializer = InconvenienceRequestLineSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(
        operation_id="retrieve_inconvenience_request_line",
        summary="Retrieve Inconvenience Request Line",
        description="Retrieve a specific Inconvenience Request Line by its ID",
        responses={
            200: InconvenienceRequestLineSerializer(),
            404: "Not Found - Inconvenience Request Line not found with the provided ID",
        }
    )
    def get(self, request, pk):
        inconvenience_request_line = get_object_or_404(InconvenienceRequestLine, pk=pk)
        serializer = InconvenienceRequestLineSerializer(inconvenience_request_line)
        return Response(serializer.data)


    @extend_schema(
        operation_id="Update Inconvenience Request Line",
        summary="Update Inconvenience Request Line",
        description="Update an existing Inconvenience Request Line by its ID.",
        request=InconvenienceRequestLineSerializer,
        responses={
            200: InconvenienceRequestLineSerializer,
            400: "Bad Request - Validation failed or ID missing",
            404: "Not Found - Inconvenience Request Line not found with the provided ID",
        }
    )
    def patch(self, request, pk=None):
        if not pk:
            return Response({"detail": "ID is required for updating"}, status=status.HTTP_400_BAD_REQUEST)
        
        inconvenience_request_line = get_object_or_404(InconvenienceRequestLine, pk=pk)
        serializer = InconvenienceRequestLineSerializer(inconvenience_request_line, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    @extend_schema(
        operation_id="Delete Inconvenience Request Line",
        summary="Delete Inconvenience Request Line",
        description="Delete an existing Inconvenience Request Line by its ID.",
        responses={
            204: "No Content - The Inconvenience Request Line was successfully deleted.",
            400: "Bad Request - ID is required for deletion",
            404: "Not Found - Inconvenience Request Line not found with the provided ID",
        }
    )
    def delete(self, request, pk=None):
        if not pk:
            return Response({"detail": "ID is required for deletion"}, status=status.HTTP_400_BAD_REQUEST)
        
        inconvenience_request_line = get_object_or_404(InconvenienceRequestLine, pk=pk)
        inconvenience_request_line.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


@extend_schema(tags=['Inconvenience Request'])
class TransitionStatusView(APIView):
    permission_classes = [IsAuthenticated]


    @extend_schema(
        operation_id="Move an inconvenience request from stage to stage",
        summary="Move an inconvenience request from stage to stage",
        description="Move an inconvenience request from stage to stage",
        request=InconvenienceRequestLineSerializer,
        responses={
            201: InconvenienceRequestLineSerializer,
            400: "Bad Request - Validation failed",
            404: "Not Found - Inconvenience Request not found with the provided ID",
        }
    )

    def post(self, request, pk):
        try:
            request_obj = InconvenienceRequest.objects.get(pk=pk)
        except InconvenienceRequest.DoesNotExist:
            return Response({'error': 'InconvenienceRequest not found'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status not in dict(InconvenienceRequest.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            request_obj.transition_status(new_status)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = InconvenienceRequestSerializer(request_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
    



