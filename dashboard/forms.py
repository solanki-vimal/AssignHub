from django import forms
from assignments.models import Assignment, Submission
from academic.models import Course, Batch

class StudentSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500',
            'placeholder': 'Search by name or email...',
            'id': 'student-search'
        })
    )

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['marks_obtained', 'faculty_remarks']
        widgets = {
            'marks_obtained': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 text-slate-900 font-semibold',
                'placeholder': 'e.g. 85',
                'step': '0.5',
                'min': '0'
            }),
            'faculty_remarks': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 text-slate-700 resize-none',
                'placeholder': 'Add feedback for the student...',
                'rows': 4
            })
        }

    def __init__(self, *args, **kwargs):
        self.max_marks = kwargs.pop('max_marks', 100)
        super().__init__(*args, **kwargs)
        self.fields['marks_obtained'].widget.attrs['max'] = self.max_marks

    def clean_marks_obtained(self):
        marks = self.cleaned_data.get('marks_obtained')
        if marks is not None and marks > self.max_marks:
            raise forms.ValidationError(f"Marks cannot exceed {self.max_marks}.")
        return marks

class FacultyCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 text-slate-700 resize-none',
                'placeholder': 'Update course description or syllabus summary...',
                'rows': 4
            })
        }

class DeadlineExtensionForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['due_date']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:border-indigo-500 font-medium'
            })
        }

class AdminBatchForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 bg-white text-slate-900'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 bg-white text-slate-900'}))
    status = forms.ChoiceField(choices=[('active', 'Active'), ('inactive', 'Inactive')], widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 bg-white text-slate-900'}))

    class Meta:
        model = Batch
        fields = ['name', 'semester']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. B7', 'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500'}),
            'semester': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 bg-white text-slate-900'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Semester is optional in model, but we want it to be a select in form
        from academic.constants import SEMESTERS
        self.fields['semester'].widget.choices = [('', '--')] + [(s, f"Sem {s}") for s in SEMESTERS]
        
        if self.instance.pk and self.instance.academic_year:
            # Try to pre-fill start/end date from academic_year (e.g. "2024-25")
            # This is an approximation since we don't store exact dates in model
            try:
                parts = self.instance.academic_year.split('-')
                self.fields['start_date'].initial = f"{parts[0]}-01-01"
                self.fields['end_date'].initial = f"20{parts[1]}-12-31"
            except: pass

    def save(self, commit=True):
        old_name = self.instance.name if self.instance.pk else None
        instance = super().save(commit=False)
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        status = self.cleaned_data.get('status')
        
        if start_date and end_date:
            s_year = str(start_date.year)
            e_year = str(end_date.year)[-2:]
            instance.academic_year = f"{s_year}-{e_year}"
        
        instance.is_active = (status == 'active')
        
        if commit:
            instance.save()
            # If batch name changed, sync the User.batch CharField for all enrolled students
            new_name = instance.name
            if old_name and old_name != new_name:
                instance.students.filter(batch=old_name).update(batch=new_name)
        return instance

class UserProfileForm(forms.ModelForm):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    class Meta:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        model = User
        fields = ['first_name', 'last_name', 'contact_no', 'enrollment_no', 'semester', 'batch', 'faculty_id', 'department', 'profile_pic']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500'}),
            'contact_no': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500', 'placeholder': '+91'}),
            'enrollment_no': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500', 'placeholder': 'e.g. 21CE000'}),
            'semester': forms.Select(choices=[('',' -- Select Semester --')] + [(i, f'Semester {i}') for i in range(1, 9)], attrs={'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 bg-white'}),
            'faculty_id': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500', 'placeholder': 'e.g. FAC001'}),
            'batch': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 bg-white'}),
            'department': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 bg-white'}),
            'profile_pic': forms.FileInput(attrs={'class': 'hidden', 'id': 'profile-pic-input', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Handle dynamic choices
        from academic.models import Batch, Department
        self.fields['batch'].queryset = Batch.objects.filter(is_archived=False).order_by('name')
        self.fields['batch'].empty_label = "-- Select Batch --"
        self.fields['department'].queryset = Department.objects.all()
        self.fields['department'].empty_label = "-- Select Department --"
        
        # We want to store names in the user model as per existing logic
        self.fields['batch'].to_field_name = 'name'
        self.fields['department'].to_field_name = 'name'

        # Restrict students from editing their own batch
        if self.instance and self.instance.role == 'student':
            self.fields['batch'].disabled = True
            self.fields['batch'].required = False
            # Optional: restrict other fields if needed, but 'batch' was specifically requested.

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # Handle M2M synchronization for Batch
            if instance.role == 'student' and instance.batch:
                from academic.models import Batch
                batch_obj = Batch.objects.filter(name=instance.batch).first()
                if batch_obj:
                    # Clear from other batches first if they should only be in one
                    instance.enrolled_batches.clear()
                    batch_obj.students.add(instance)
        return instance
