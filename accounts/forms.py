from django import forms
from django.contrib.auth import get_user_model
from academic.models import Department, Batch

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    """
    Unified registration form for Student and Faculty accounts.
    Admin accounts are blocked from registering through this form for security.
    """

    # --- Custom fields (not directly on the User model) ---

    full_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your full name',
            'class': 'w-full pl-10 py-5 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:bg-white focus:border-teal-500 transition-colors'
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',
            'class': 'w-full pl-10 py-5 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:bg-white focus:border-teal-500 transition-colors'
        })
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'id': 'password-input',
            'class': 'w-full pl-10 pr-12 py-5 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:bg-white focus:border-teal-500 transition-colors'
        })
    )

    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your password',
            'id': 'confirm-password-input',
            'class': 'w-full pl-10 pr-12 py-5 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:bg-white focus:border-teal-500 transition-colors'
        })
    )

    # Dropdown populated from the Department model in the DB.
    # The selected object's .name is synced to User.department in save().
    department_choice = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="Select Department",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-5 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:bg-white focus:border-teal-500 transition-colors'
        })
    )

    class Meta:
        model = User
        # These model fields are rendered directly by Django
        fields = ['role', 'contact_no', 'enrollment_no', 'faculty_id', 'department']
        widgets = {
            'role': forms.HiddenInput(),            # Set by JS when user picks Student/Faculty
            'contact_no': forms.TextInput(attrs={
                'placeholder': 'e.g., +91 98765 43210',
                'class': 'w-full px-4 py-5 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:bg-white focus:border-teal-500 transition-colors'
            }),
            'enrollment_no': forms.TextInput(attrs={  # Visible only for Students
                'placeholder': 'e.g., 24CEUBS148',
                'class': 'w-full px-4 py-5 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:bg-white focus:border-teal-500 transition-colors'
            }),
            'faculty_id': forms.TextInput(attrs={     # Visible only for Faculty
                'placeholder': 'e.g., FAC101',
                'class': 'w-full px-4 py-5 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:bg-white focus:border-teal-500 transition-colors'
            }),
            'department': forms.HiddenInput(),        # Synced from department_choice in save()
        }

    def clean(self):
        """Validates password match, unique email, and blocks admin registration."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        email = cleaned_data.get("email")
        role = cleaned_data.get("role")

        # Ensure both passwords match
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

        # Prevent duplicate accounts (username = email in this system)
        if email and User.objects.filter(username=email).exists():
            self.add_error('email', "A user with this email already exists")

        # Security: block admin creation via the public registration form
        if role == 'admin':
            self.add_error('role', "Admin accounts cannot be created via the public registration form.")

        return cleaned_data

    def save(self, commit=True):
        """Creates the User with hashed password and syncs department from the dropdown."""
        user = super().save(commit=False)

        # Use email as both username and email (single-credential login)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']

        # Hash the password securely
        user.set_password(self.cleaned_data['password'])

        # Store full_name into first_name
        user.first_name = self.cleaned_data['full_name']

        # Sync the Department model object's name to User.department CharField
        dept = self.cleaned_data.get('department_choice')
        if dept:
            user.department = dept.name

        if commit:
            user.save()

        return user
