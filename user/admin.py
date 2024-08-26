from django.contrib import admin
from .models import User,Department
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import CustomUserChangeForm, CustomUserCreationForm


class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('email', 'first_name', 'last_name', 'department', 'staff_id', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'department', 'groups')
    search_fields = ('email', 'first_name', 'last_name', 'staff_id')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'department', 'staff_id')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions', 'groups')}),
        
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'department', 'staff_id', 'password1', 'password2', 'groups'),
        }),
    )
    filter_horizontal = ('user_permissions',)


admin.site.register(User, CustomUserAdmin)
# Register your models here.
# admin.site.register(User, UserAdmin)
admin.site.register(Department)


