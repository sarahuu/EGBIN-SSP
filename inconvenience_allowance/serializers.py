from rest_framework import serializers
from .models import InconvenienceRequest, InconvenienceRequestLine, Day
from egbin_ssp.exceptions import SerializerValidationException
from django.shortcuts import get_object_or_404
from user.models import User
from rest_framework.exceptions import PermissionDenied


class DaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Day
        fields = '__all__'



class BulkInconvenienceRequestLineSerializer(serializers.ListSerializer):
    
    def create_or_update_instance(self, validated_data, inconvenience_request):
        validated_data['job_description'] = inconvenience_request.description
        day_instances = validated_data.get('dates')

        # Use `update_or_create` for single instance
        instance, created = InconvenienceRequestLine.objects.update_or_create(
            id=validated_data.get('id'),
            defaults={
                'inconvenience_request': inconvenience_request,
                'employee': validated_data.get('employee'),
                'job_description':inconvenience_request.description
            }
        )
        instance.days.set(day_instances)  # Set the Many-to-Many field
        instance.save()
        return instance



    def validate_data(self, data,creator,invalid_days:set, invalid_employees:list, booked_dates:list):
        
        #validate employee
        employee = User.objects.get(id=data["employee"].id)
        if employee and creator.department != employee.department:
            invalid_employees.append(employee)
            # raise PermissionDenied(f"{employee.first_name} does not belong to your department")

        #validate dates
        days = data.get('dates', [])
        day_instances = []
        for date in days:
            try:
                day_instance = Day.objects.get(date=date)
                day_instances.append(day_instance)
            except:
                invalid_days.add(str(date))
        
            # Check each date in the list to ensure none have been booked with a non-draft status
        for date in day_instances:
            # Filter for existing bookings
            bookings = InconvenienceRequestLine.objects.filter(
                employee=data['employee'],
                days=date  # Assumes days__date is the correct field to filter on
            )
            
            if bookings.exists():  # Check if any bookings are found
                message = f"{data['employee'].first_name} cannot be booked for {date.date} as they have already been booked for that day."
                booked_dates.append(message)
            data['dates'] = day_instances
        return data

    def create(self, validated_data):
        inconvenience_request_id = self.context.get('inconvenience_request_id')
        inconvenience_request = InconvenienceRequest.objects.get(id=inconvenience_request_id)
        invalid_days = set()
        invalid_employees = set()
        booked_dates = []
        error_list = []
        if isinstance(validated_data, list):
            # Bulk create list of instances
            inconvenience_request_lines = []
            for data in validated_data:
                #validate data
                self.validate_data(data,self.context.get('user'),invalid_days,invalid_employees,booked_dates)
           
            if invalid_days:
                dates = ",".join(invalid_days)
                message = f"Dates: {dates} are not available for reservation"
                error_list.append(message)
            if invalid_employees:
                error_list.extend(invalid_employees)
            if booked_dates:
                error_list.extend(booked_dates)
            
            if error_list:
                raise SerializerValidationException(detail=error_list,code=400)
            for data in validated_data:
                instance = self.create_or_update_instance(data, inconvenience_request)
                inconvenience_request_lines.append(instance)
            return inconvenience_request_lines
        else:
            self.validate_data(validated_data,self.context.get('user'),invalid_days,invalid_employees,booked_dates)
            if invalid_days:
                error_list.extend(invalid_days)
            if invalid_employees:
                error_list.extend(invalid_employees)
            if booked_dates:
                error_list.extend(booked_dates)
            
            if error_list:
                raise SerializerValidationException(detail=error_list,code=400)

            return self.create_or_update_instance(validated_data, inconvenience_request)





class InconvenienceRequestLineSerializer(serializers.ModelSerializer):
    dates = serializers.ListField(
            child=serializers.DateField(),
            required=False, write_only=True
        )
    days = DaySerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    employee_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = InconvenienceRequestLine
        fields = ['id', 'inconvenience_request', 'job_description', 'employee','employee_name', 'days', 'no_of_weekend', 'no_of_ph', 'no_of_days', 'amount', 'response', 'response_time', 'attendance_status', 'created_at', 'dates', 'status']
        list_serializer_class = BulkInconvenienceRequestLineSerializer
        extra_kwargs = {
            'inconvenience_request':{'read_only':True},
            'job_description': {'required': False,'read_only':True},
            'no_of_weekend': {'read_only': True},
            'no_of_ph': {'read_only': True},
            'no_of_days': {'read_only': True},
            'amount': {'read_only': True},
            'response_time': {'read_only': True},
            'attendance_status': {'read_only': True},
            'created_at': {'read_only': True}
        }
    def get_status(self, obj):
        return obj.inconvenience_request.status if obj.inconvenience_request else None

    def get_employee_name(self, obj):
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return None
    def to_internal_value(self, data):
        # Validate the employee field
        employee_id = data.get('employee')
        if employee_id:
            try:
                pos = User.objects.get(pk=employee_id)
            except User.DoesNotExist:
                # Customize the error message here
                raise SerializerValidationException(f"Employee with id {employee_id} does not exist. Contact Support")
    
        validated_data = super().to_internal_value(data)
        return validated_data



class InconvenienceRequestSerializer(serializers.ModelSerializer):
    lines = InconvenienceRequestLineSerializer(many=True,read_only=True)

    class Meta:
        model = InconvenienceRequest
        fields = ['id', 'request_id', 'title', 'description', 'department', 'department_rep', 'created_at', 'updated_at', 'status','lines']
        extra_kwargs = {
            'request_id':{'read_only':True},
            'department': {'read_only': True},
            'department_rep':{'read_only':True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'status': {'read_only': True}
        }
        
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['department_rep'] = request.user
        validated_data['department'] = request.user.department

        # Call super to handle the actual creation
        return super().create(validated_data)
    

class TransitionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=InconvenienceRequest.STATUS_CHOICES)

class ErrorResponseSerializer(serializers.Serializer):
    status_code = serializers.IntegerField()
    errors = serializers.ListField()