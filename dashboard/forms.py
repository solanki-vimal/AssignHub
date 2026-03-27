"""
Forms for the dashboard app.

Contains forms used across all dashboard views:
  - StudentSearchForm: Search/filter students
  - EvaluationForm: Faculty grading of submissions
  - FacultyCourseForm: Faculty course description editing
  - DeadlineExtensionForm: Faculty deadline extension
  - AdminBatchForm: Admin batch creation/editing with sync logic
  - UserProfileForm: Profile editing for all roles
"""

from django import forms
from django.contrib.auth import get_user_model
from assignments.models import Assignment, Submission
from academic.models import Course, Batch, Department

User = get_user_model()


# =============================================================================
# Faculty Forms
# =============================================================================

class StudentSearchForm(forms.Form):
    """Simple text search for filtering students by name or email."""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500',
            'placeholder': 'Search by name or email...',
            'id': 'student-search'
        })
    )


class EvaluationForm(forms.ModelForm):
    """
    Form for faculty to grade a student's submission.
    Accepts 'max_marks' kwarg to dynamically cap the marks input.
    """

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
        """Validates that marks don't exceed the assignment's max_marks."""
        marks = self.cleaned_data.get('marks_obtained')
        if marks is not None and marks > self.max_marks:
            raise forms.ValidationError(f"Marks cannot exceed {self.max_marks}.")
        return marks


class FacultyCourseForm(forms.ModelForm):
    """Allows faculty to update their course description."""

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
    """Minimal form to extend an assignment's due_date via a datetime picker."""

    class Meta:
        model = Assignment
        fields = ['due_date']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:border-indigo-500 font-medium'
            })
        }


# =============================================================================
# Admin Forms
# =============================================================================

class AdminBatchForm(forms.ModelForm):
    """
    Form for admins to create/edit batches.
    Adds custom start_date, end_date, and status fields, which are
    converted to/from the model's academic_year and is_active fields.
    Also syncs User.batch CharField when a batch name changes.
    """

    start_date = forms.DateField(widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 bg-white text-slate-900'
    }))
    end_date = forms.DateField(widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 bg-white text-slate-900'
    }))
    status = forms.ChoiceField(
        choices=[('active', 'Active'), ('inactive', 'Inactive')],
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 bg-white text-slate-900'
        })
    )

    class Meta:
        model = Batch
        fields = ['name', 'semester']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. B7',
                'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500'
            }),
            'semester': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 bg-white text-slate-900'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate semester dropdown from project constants
        from academic.constants import SEMESTERS
        self.fields['semester'].widget.choices = [('', '--')] + [(s, f"Sem {s}") for s in SEMESTERS]

        # Pre-fill start/end dates from academic_year (e.g., "2024-25")
        if self.instance.pk and self.instance.academic_year:
            try:
                parts = self.instance.academic_year.split('-')
                self.fields['start_date'].initial = f"{parts[0]}-01-01"
                self.fields['end_date'].initial = f"20{parts[1]}-12-31"
            except:
                pass

    def save(self, commit=True):
        """
        Converts start/end dates → academic_year string (e.g., "2024-25").
        Syncs User.batch CharField if the batch name was changed.
        """
        old_name = self.instance.name if self.instance.pk else None
        instance = super().save(commit=False)

        # Build academic_year from date fields (e.g., 2024-01-01 → 2025-12-31 = "2024-25")
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
            # If batch name changed, update User.batch for all enrolled students
            new_name = instance.name
            if old_name and old_name != new_name:
                instance.students.filter(batch=old_name).update(batch=new_name)

        return instance


# =============================================================================
# Shared Forms (All Roles)
# =============================================================================

class UserProfileForm(forms.ModelForm):
    """
    Profile editing form for all roles (student, faculty, admin).
    Dynamically populates batch and department dropdowns from the DB.
    Students cannot edit their own batch (set by admin only).
    """

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'contact_no',
            'enrollment_no', 'semester', 'batch',
            'faculty_id', 'department', 'profile_pic'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500'}),
            'contact_no': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500', 'placeholder': '+91'}),
            'enrollment_no': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500', 'placeholder': 'e.g. 21CE000'}),
            'semester': forms.Select(
                choices=[('', ' -- Select Semester --')] + [(i, f'Semester {i}') for i in range(1, 9)],
                attrs={'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 bg-white'}
            ),
            'faculty_id': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500', 'placeholder': 'e.g. FAC001'}),
            'batch': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 bg-white'}),
            'department': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-indigo-500 bg-white'}),
            'profile_pic': forms.FileInput(attrs={'class': 'hidden', 'id': 'profile-pic-input', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate batch and department dropdowns from DB
        self.fields['batch'].queryset = Batch.objects.filter(is_archived=False).order_by('name')
        self.fields['batch'].empty_label = "-- Select Batch --"
        self.fields['department'].queryset = Department.objects.all()
        self.fields['department'].empty_label = "-- Select Department --"

        # Store name strings (not FK IDs) in the User model
        self.fields['batch'].to_field_name = 'name'
        self.fields['department'].to_field_name = 'name'

        # Students cannot edit their own batch (managed by admin)
        if self.instance and self.instance.role == 'student':
            self.fields['batch'].disabled = True
            self.fields['batch'].required = False

    def save(self, commit=True):
        """Saves profile and syncs M2M Batch enrollment for students."""
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # Sync M2M: ensure student is enrolled in the correct Batch
            if instance.role == 'student' and instance.batch:
                batch_obj = Batch.objects.filter(name=instance.batch).first()
                if batch_obj:
                    instance.enrolled_batches.clear()
                    batch_obj.students.add(instance)
        return instance
