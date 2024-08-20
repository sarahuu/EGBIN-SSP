# users/serializers.py

from rest_framework import serializers
from .models import User,Department

class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_active', 'is_staff','department','staff_id','groups')

    def get_groups(self, obj):
        return obj.groups.values_list('name', flat=True)


class RegisterUserSerializer(serializers.ModelSerializer):
    department_id = serializers.IntegerField()

    class Meta:
        model = User
        fields = ('id','email', 'password', 'first_name', 'last_name', 'department_id','staff_id')
        extra_kwargs = {'password': {'write_only': True}, 'staff_id':{'required':False}}

    def create(self, validated_data):
        department_id = validated_data.pop('department_id')
        
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            raise serializers.ValidationError("Department with this ID does not exist.")

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            department=department)

        return user
    
    def update(self, instance, validated_data):
        department_id = validated_data.pop('department_id', None)
        if department_id:
            try:
                department = Department.objects.get(id=department_id)
                instance.department = department
            except Department.DoesNotExist:
                raise serializers.ValidationError("Department with this ID does not exist.")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']    