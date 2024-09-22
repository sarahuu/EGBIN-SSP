from rest_framework import status, viewsets, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import InconvenienceRequest, InconvenienceRequestLine, Day
from .serializers import InconvenienceRequestSerializer,InconvenienceRequestLineSerializer, DaySerializer, TransitionSerializer, ErrorResponseSerializer, BulkInconvenienceRequestLineSerializer
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied
from egbin_ssp.exceptions import SerializerValidationException

@extend_schema(tags=['Days'])
class DayViewSet(viewsets.ModelViewSet):
    queryset = Day.objects.all()
    serializer_class = DaySerializer

    @extend_schema(
        operation_id="list_days",
        summary="Retrieve a list of days",
        description="Fetch all day records in the system.",
        responses={200: DaySerializer(many=True), 400:ErrorResponseSerializer},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        operation_id="create_day",
        summary="Create a new day",
        description="Create a new day record.",
        request=DaySerializer,
        responses={201: DaySerializer,400:ErrorResponseSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        operation_id="retrieve_day",
        summary="Retrieve a day",
        description="Fetch a specific day by ID.",
        responses={200: DaySerializer,400:ErrorResponseSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


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
        responses={201: InconvenienceRequestSerializer,400:ErrorResponseSerializer},
    )
    def post(self, request):
        if not request.user.groups.filter(name='Department Representatives').exists():
            raise SerializerValidationException("Not Permitted",code=403)
        
        data = request.data
        serializer = InconvenienceRequestSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise SerializerValidationException(serializer.errors,code=400)
    

    @extend_schema(
        operation_id="List Inconvenience Request",
        summary="List Inconvenience Request",
        description="List all Inconvenience Requests",
        responses={
            200: InconvenienceRequestSerializer(many=True),
            400: ErrorResponseSerializer,
        }
    )
    def get(self, request):
        if request.user.groups.filter(name='Department Representatives').exists():
            inconvenience_requests = InconvenienceRequest.objects.filter(department=request.user.department)
        elif request.user.groups.filter(name='HR').exists():
            # HR can view all records
            inconvenience_requests = InconvenienceRequest.objects.all().exclude(status='draft')
        elif request.user.groups.filter(name='Line Managers').exists() or \
             request.user.groups.filter(name='Employees').exists():
            # Other roles can view only their department records
            inconvenience_requests = InconvenienceRequest.objects.filter(department=request.user.department).exclude(status='draft')
        else:
            raise SerializerValidationException("Not Permitted",code=403)
        
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
            400: ErrorResponseSerializer,
        }
    )
    def get(self, request, pk):
        inconvenience_request = get_object_or_404(InconvenienceRequest, pk=pk)
        if request.user.groups.filter(name='HR').exists():
            # HR can view all requests
            if inconvenience_request.status == 'draft':
                raise PermissionDenied("Not permitted to access this request.")
            serializer = InconvenienceRequestSerializer(inconvenience_request)

        elif request.user.groups.filter(name='Line Managers').exists():
            # Department Reps and Line Managers can view requests for their department
            if inconvenience_request.department != request.user.department or inconvenience_request.status == 'draft':
                raise PermissionDenied("Not permitted to access this request.")
            serializer = InconvenienceRequestSerializer(inconvenience_request)

        elif request.user.groups.filter(name='Department Representatives').exists():
            # Department Reps and Line Managers can view requests for their department
            if inconvenience_request.department != request.user.department:
                raise PermissionDenied("Not permitted to access this request.")
            serializer = InconvenienceRequestSerializer(inconvenience_request)
            
        else:
            # Employees can view their own requests if they belong to the same department
            if inconvenience_request.department != request.user.department or inconvenience_request.status=="draft":
                raise PermissionDenied("Not permitted to access this request.")
            serializer = InconvenienceRequestSerializer(inconvenience_request)
        return Response(serializer.data)


    @extend_schema(
        operation_id="Update Inconvenience Request",
        summary="Update Inconvenience Request",
        description="Update an existing Inconvenience Request by its ID.",
        request=InconvenienceRequestSerializer,
        responses={
            200: InconvenienceRequestSerializer,
            400: ErrorResponseSerializer,
        }
    )
    def put(self, request, pk=None):
        if not pk:
            raise SerializerValidationException("ID is required for updating")
        inconvenience_request = get_object_or_404(InconvenienceRequest, pk=pk)
        # Check permissions
        user = request.user
        if not (user.groups.filter(name='Department Representatives').exists() or 
                user.groups.filter(name='Line Managers').exists() or 
                user.groups.filter(name='HR').exists()):
            raise PermissionDenied("Not permitted to update records.")
        
        # Check if user is authorized to update this record
        if not (user.groups.filter(name='HR').exists() or 
                (user.groups.filter(name='Department Representatives').exists() and 
                inconvenience_request.department == user.department) or 
                (user.groups.filter(name='Line Managers').exists() and 
                inconvenience_request.department == user.department)):
            raise PermissionDenied("Not permitted to update this request.")
        
        #ensure only department rep can edit request when in draft state
        if not user.groups.filter(name='Department Representatives') and inconvenience_request.status == 'draft':
            raise PermissionDenied("Not permitted to update this request.")
        
        # Serialize the data
        serializer = InconvenienceRequestSerializer(inconvenience_request, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        raise SerializerValidationException(serializer.errors,code=400)


    @extend_schema(
        operation_id="Delete Inconvenience Request",
        summary="Delete Inconvenience Request",
        description="Delete an existing Inconvenience Request by its ID.",
        responses={
            204: None,
            400: ErrorResponseSerializer,
        }
    )
    def delete(self, request, pk=None):
        if not pk:
            raise SerializerValidationException("ID is required for deletion")
        
        inconvenience_request = get_object_or_404(InconvenienceRequest, pk=pk)
        user = request.user
        if not (user.groups.filter(name='Department Representatives').exists() or 
                user.groups.filter(name='Line Managers').exists() or 
                user.groups.filter(name='HR').exists()):
            raise PermissionDenied("Not permitted to delete records.")
        
        if not (user.groups.filter(name='HR').exists() or 
                (user.groups.filter(name='Department Representatives').exists() and 
                inconvenience_request.department == user.department) or 
                (user.groups.filter(name='Line Managers').exists() and 
                inconvenience_request.department == user.department)):
            raise PermissionDenied("Not permitted to delete this request.")

        #ensure only department rep can delete request when in draft state
        if not user.groups.filter(name='Department Representatives') and inconvenience_request.status == 'draft':
            raise PermissionDenied("Not permitted to delete this request.")

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
            400: ErrorResponseSerializer
        }
    )
    def get(self, request):
        user = request.user
        # Check for HR role
        if user.groups.filter(name='HR').exists():
            # HR can view all request lines
            inconvenience_request_lines = InconvenienceRequestLine.objects.all().exclude(inconvenience_request__status='draft')
        # Check for Line Managers roles
        elif user.groups.filter(name='Line Managers').exists():
            # Filter request lines by department
            inconvenience_request_lines = InconvenienceRequestLine.objects.filter(inconvenience_request__department=user.department).exclude(inconvenience_request__status="draft")
        # Check for Department Manager roles
        elif user.groups.filter(name='Department Representatives').exists():
            # Filter request lines by department
            inconvenience_request_lines = InconvenienceRequestLine.objects.filter(inconvenience_request__department=user.department)
        # Check for Employee role
        elif user.groups.filter(name='Employees').exists():
            # Filter request lines by department
            inconvenience_request_lines = InconvenienceRequestLine.objects.filter(inconvenience_request__department=user.department).exclude(inconvenience_request__status="draft")
        
        else:
            # If user role is not valid, return Forbidden response
            raise SerializerValidationException("Not permitted to view request lines.",code=403)
        
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
            201: InconvenienceRequestLineSerializer(many=True),
            400: ErrorResponseSerializer,
            404: "Not Found - Inconvenience Request not found with the provided ID",
        }
    )
    def post(self, request, pk):
        try:
            inconvenience_request = InconvenienceRequest.objects.get(id=pk)
        except InconvenienceRequest.DoesNotExist:
            raise SerializerValidationException('Inconvenience Request not found')
        

        # Permission check
        user = request.user
        if not (user.groups.filter(name='Department Representatives').exists() or 
                user.groups.filter(name='Line Managers').exists() or 
                user.groups.filter(name='HR').exists()):
            raise SerializerValidationException("Not permitted to create request lines.",code=403)
        
        # Ensure the user is authorized to create a request line for this inconvenience request
        if not (user.groups.filter(name='HR').exists() or 
                (user.groups.filter(name='Department Representatives').exists() and 
                inconvenience_request.department == user.department) or 
                (user.groups.filter(name='Line Managers').exists() and 
                inconvenience_request.department == user.department)):
            raise SerializerValidationException("Not permitted to create a request line for this request.",code=403)
        
        
        #ensure that only department rep can create inconvenience line when the request is in draft stage
        if not user.groups.filter(name="Department Representatives").exists() and inconvenience_request.status == "draft":
            raise SerializerValidationException("Not permitted to create a request line for this request.",code=403)
        
        data = request.data
        if isinstance(data, list):
            serializer = InconvenienceRequestLineSerializer(data=data, context={'inconvenience_request_id': inconvenience_request.id,'user':request.user}, many=True)
            print(data)
        else:
            serializer = InconvenienceRequestLineSerializer(data=data, context={'inconvenience_request_id': inconvenience_request.id, 'user':request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        raise SerializerValidationException(serializer.errors,code=400)


    @extend_schema(
        operation_id="retrieve_inconvenience_request_line",
        summary="Retrieve Inconvenience Request Line",
        description="Retrieve a specific Inconvenience Request Line by its ID",
        responses={
            200: InconvenienceRequestLineSerializer,
            404: ErrorResponseSerializer,
        }
    )
    def get(self, request, pk):
        # Retrieve the specific Inconvenience Request Line
        inconvenience_request_line = get_object_or_404(InconvenienceRequestLine, pk=pk)
        
        # Permission check
        user = request.user

        if inconvenience_request_line.inconvenience_request.status == 'draft' and not user.groups.filter(name="Department Representatives"):
            raise SerializerValidationException("Not permitted to view this request line.",code=403)
        
        # Check if the user is HR or is related to the department of the request line
        if user.groups.filter(name='HR').exists():
            # HR can view all request lines
            serializer = InconvenienceRequestLineSerializer(inconvenience_request_line)
            return Response(serializer.data)
        
        if user.groups.filter(name='Department Representatives').exists() or \
        user.groups.filter(name='Line Managers').exists() or \
        user.groups.filter(name='Employees').exists():
            # Check if the request line belongs to the user's department
            if inconvenience_request_line.department == user.department:
                serializer = InconvenienceRequestLineSerializer(inconvenience_request_line)
                return Response(serializer.data)
            else:
                return Response({"detail": "Not permitted to view this request line."}, status=status.HTTP_403_FORBIDDEN)
        
        # If user role is not valid, return Forbidden response
        raise SerializerValidationException("Not permitted to view request lines.",code=403)


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
            raise SerializerValidationException("ID is required for deletion")
        
        inconvenience_request_line = get_object_or_404(InconvenienceRequestLine, pk=pk)
    # Permission check
        user = request.user
        
        if inconvenience_request_line.inconvenience_request.status == 'draft' and not user.groups.filter(name="Department Representatives"):
            return Response({"detail": "Not permitted to view this request line."}, status=status.HTTP_403_FORBIDDEN)
        
        if user.groups.filter(name='HR').exists():
            # HR can delete any request line
            inconvenience_request_line.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        if user.groups.filter(name='Department Representatives').exists() or \
        user.groups.filter(name='Line Managers').exists():
            inconvenience_request_line.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        # Employees cannot delete request lines
        raise SerializerValidationException("Not permitted to delete request lines.",code=403)




@extend_schema(tags=['Inconvenience Request Lines'])
class InconvenienceRequestLineOwnView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="List Current User's Inconvenience Requests",
        summary="List Current User's Inconvenience Requests",
        description="List Current User's Inconvenience Requests",
        responses={
            200: InconvenienceRequestLineSerializer(many=True),
            400: ErrorResponseSerializer

        }
    )
    def get(self, request):
        inconvenience_request_lines = InconvenienceRequestLine.objects.filter(employee=request.user.id).exclude(inconvenience_request__status="draft")
        serializer = InconvenienceRequestLineSerializer(inconvenience_request_lines, many=True)
        return Response(serializer.data)



@extend_schema(tags=['Inconvenience Request'])
class TransitionStatusView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        operation_id="Move an inconvenience request from stage to stage",
        summary="Move an inconvenience request from stage to stage",
        description=
        """
        Moves an inconvenience request from one stage to another within the workflow.

        This function facilitates the transition of an inconvenience request through 
        various stages, ensuring that each transition adheres to the predefined valid 
        transitions. The stages are part of a structured workflow, and only certain 
        transitions are allowed.

        Stages:
        -------
        The possible stages in the workflow are:
        - draft: The request is in draft state.
        - submitted: The request has been submitted for approval.
        - manager_approved: The request has been approved by the manager.
        - work_done: The required work has been completed.
        - hr_approval: The HR department is reviewing the request.
        - completed: The request has been finalized and marked as completed.
        - rejected: The request has been rejected.

        Valid Transitions:
        ------------------
        The request can only move between stages based on the following rules:
        - draft -> submitted
        - submitted -> manager_approved, rejected
        - manager_approved -> work_done
        - work_done -> hr_approval
        - hr_approval -> completed

        Parameters:
        -----------
        id : int
            The unique identifier of the inconvenience request to be moved.
        status : str
            The stage to which the request should be moved. Must be one of the 
            valid stages as outlined above.
        """

        
        
        
        ,
        request=TransitionSerializer,
        responses={
            201: InconvenienceRequestSerializer,
            400: ErrorResponseSerializer,
        }
    )

    def post(self, request, pk):
        if not pk:
            raise SerializerValidationException("ID is required for updating status")
        
        try:
            request_obj = InconvenienceRequest.objects.get(pk=pk)
        except InconvenienceRequest.DoesNotExist:
            raise SerializerValidationException('InconvenienceRequest not found',code=404)

        user = request.user
        new_status = request.data.get('status')

        if new_status not in dict(InconvenienceRequest.STATUS_CHOICES):
            raise SerializerValidationException('Invalid status')

        current_status = request_obj.status
        
        if user.groups.filter(name='Department Representatives').exists():
            if current_status == 'draft' and new_status == 'submitted':
                request_obj.transition_status(new_status)
            else:
                raise SerializerValidationException("Not permitted to transition to this status",code=403)
        
        elif user.groups.filter(name='Line Managers').exists():
            if current_status == 'submitted' and new_status == 'manager_approved':
                request_obj.transition_status(new_status)
            elif current_status == 'manager_approved' and new_status == 'work_done':
                request_obj.transition_status(new_status)
            else:
                raise SerializerValidationException("Not permitted to transition to this status",code=403)

        elif user.groups.filter(name='HR').exists():
            if current_status == 'work_done' and new_status == 'hr_approval':
                request_obj.transition_status(new_status)
                request_obj.transition_status('completed')
            else:
                raise SerializerValidationException("Not permitted to transition to this status",code=403)
        
        else:
            raise SerializerValidationException('Not authorized to update status', code=403)

        serializer = InconvenienceRequestSerializer(request_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)