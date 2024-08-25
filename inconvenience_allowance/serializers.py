from rest_framework import serializers
from .models import InconvenienceRequest, InconvenienceRequestLine, Day
from datetime import datetime
import datetime as dt


class DaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Day
        fields = '__all__'

class InconvenienceRequestLineSerializer(serializers.ModelSerializer):
    dates = serializers.ListField(
            child=serializers.DateField(),
            required=False, write_only=True
        )
    days = DaySerializer(many=True, read_only=True)

    class Meta:
        model = InconvenienceRequestLine
        fields = ['id', 'inconvenience_request', 'job_description', 'employee', 'days', 'no_of_weekend', 'no_of_ph', 'no_of_days', 'amount', 'response', 'response_time', 'attendance_status', 'created_at', 'dates']

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


    def validate(self, data):
        days = data.get('dates', [])

        # Check each date in the list to ensure none have been booked with a non-draft status
        for date in days:
            # print(InconvenienceRequestLine.objects.filter(employee__id=data['employee']))
            if InconvenienceRequestLine.objects.filter(
                    employee=data['employee'],
                    days__date=[datetime.strptime(date, '%Y-%m-%d').date()]  # Assumes booking_dates is a list field in the model
            ):
                raise serializers.ValidationError(f"You cannot book for {date} as you have already been booked for that day")
 
        return data

    def create(self, validated_data):
        inconvenience_request_id = self.context.get('inconvenience_request_id')
        
        # Retrieve the inconvenience request instance
        try:
            inconvenience_request = InconvenienceRequest.objects.get(id=inconvenience_request_id)
            validated_data['inconvenience_request'] = inconvenience_request
        except InconvenienceRequest.DoesNotExist:
            raise serializers.ValidationError("Inconvenience request does not exist.")
        
        days_data = validated_data.pop('dates', [])
        try:
            day_instances = [Day.objects.get(date=date) for date in days_data]
        except:
            raise serializers.ValidationError("Some of the provided dates do not correspond to existing days.")


        validated_data['job_description'] = validated_data['inconvenience_request'].description

        inconvenience_request_line = InconvenienceRequestLine.objects.create(**validated_data)
        inconvenience_request_line.days.set(day_instances)
                
        inconvenience_request_line.save()
        return inconvenience_request_line
    

    def update(self, instance, validated_data):
        days_data = validated_data.pop('dates', [])
        
        # Update fields on the instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Handle days update
        if days_data is not None:
            try:
                day_instances = [Day.objects.get(date=date) for date in days_data]
            except:
                raise serializers.ValidationError("Some of the provided dates do not correspond to existing days.")
                    
            instance.days.set(day_instances)

            # Retrieve the existing days
            current_days = set(instance.days.values_list('date', flat=True))
            days_to_remove = Day.objects.filter(date__in=current_days)
            
            # Update the days relationship
            instance.days.remove(*days_to_remove) #remove all existing days
            instance.days.set(day_instances) #add all new days
        
        instance.save()
        return instance
        






class InconvenienceRequestSerializer(serializers.ModelSerializer):
    lines = InconvenienceRequestLineSerializer(many=True, read_only=True)

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