from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'account_status', 'is_staff')
    list_filter = ('role', 'account_status', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role', 'contact_no', 'account_status', 'enrollment_no', 'faculty_id', 'department')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role', 'contact_no', 'account_status', 'enrollment_no', 'faculty_id', 'department')}),
    )

admin.site.register(User, CustomUserAdmin)
