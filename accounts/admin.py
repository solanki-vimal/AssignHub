from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for the AssignHub User model.
    Extends Django's built-in UserAdmin to include role-specific fields
    such as enrollment_no (students), faculty_id (faculty), and account_status.
    """

    # Columns shown in the admin user list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'account_status', 'is_staff')

    # Sidebar filter options in the user list view
    list_filter = ('role', 'account_status', 'is_staff', 'is_superuser', 'is_active')

    # Extends the default edit form with AssignHub-specific fields
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role', 'contact_no', 'account_status', 'enrollment_no', 'faculty_id', 'department')}),
    )

    # Extends the "Add New User" form with the same role-specific fields
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role', 'contact_no', 'account_status', 'enrollment_no', 'faculty_id', 'department')}),
    )


# Register the custom User model with the custom admin configuration
admin.site.register(User, CustomUserAdmin)