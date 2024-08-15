from rest_framework import permissions
from django.contrib.auth.models import Group

class IsDepartmentRep(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Department Representatives').exists()

class IsHR(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='HR').exists()

class IsLineManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Line Managers').exists()

class IsEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Employees').exists()


class IsInDepartment(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Assuming `department` is a ForeignKey or related field in your model
        if request.user.groups.filter(name='HR').exists():
            return True  # HR can view all records

        if request.user.groups.filter(name='Department Representatives').exists():
            return obj.department == request.user.department

        if request.user.groups.filter(name='Line Managers').exists():
            return obj.department == request.user.department

        if request.user.groups.filter(name='Employees').exists():
            return obj.department == request.user.department

        return False
