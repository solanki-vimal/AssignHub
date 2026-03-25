from django import forms
from django.contrib.auth import get_user_model
from academic.models import Department, Batch

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
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
    
    # Dynamic selections from DB
    department_choice = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="Select Department",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-5 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:bg-white focus:border-teal-500 transition-colors'
        })
    )
    
    batch_choice = forms.ModelChoiceField(
        queryset=Batch.objects.all(),
        required=False,
        empty_label="Select Batch",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-5 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:bg-white focus:border-teal-500 transition-colors'
        })
    )

    class Meta:
        model = User
        fields = ['role', 'contact_no', 'enrollment_no', 'faculty_id', 'department', 'batch']
        widgets = {
            'role': forms.HiddenInput(),
            'contact_no': forms.TextInput(attrs={
                'placeholder': 'e.g., +91 98765 43210', 
                'class': 'w-full px-4 py-5 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:bg-white focus:border-teal-500 transition-colors'
            }),
            'enrollment_no': forms.TextInput(attrs={
                'placeholder': 'e.g., 24CEUBS148', 
                'class': 'w-full px-4 py-5 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:bg-white focus:border-teal-500 transition-colors'
            }),
            'faculty_id': forms.TextInput(attrs={
                'placeholder': 'e.g., FAC101', 
                'class': 'w-full px-4 py-5 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:bg-white focus:border-teal-500 transition-colors'
            }),
            'department': forms.HiddenInput(),
            'batch': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        email = cleaned_data.get("email")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")
        
        if email and User.objects.filter(username=email).exists():
            self.add_error('email', "A user with this email already exists")
            
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        user.first_name = self.cleaned_data['full_name']
        
        # Sync the dynamic choice names to the model CharFields
        dept = self.cleaned_data.get('department_choice')
        if dept:
            user.department = dept.name
            
        batch_obj = self.cleaned_data.get('batch_choice')
        if batch_obj:
            user.batch = batch_obj.name

        if commit:
            user.save()
            # If it's a student, add them to the Batch M2M
            if user.role == 'student' and batch_obj:
                batch_obj.students.add(user)
                
        return user
