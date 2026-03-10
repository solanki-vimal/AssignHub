from django import forms
from .models import Assignment
from academic.models import Course, Batch

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'course', 'batch', 'start_date', 'due_date', 'max_marks', 'max_file_size_mb', 'late_policy', 'published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'e.g. Lab 3: UML Diagrams'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500',
                'rows': 4,
                'placeholder': 'Describe the assignment...'
            }),
            'course': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500'
            }),
            'batch': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500',
                'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500',
                'type': 'date'
            }),
            'max_marks': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': '100'
            }),
            'max_file_size_mb': forms.Select(choices=[(5, '5 MB'), (10, '10 MB'), (25, '25 MB'), (50, '50 MB'), (100, '100 MB')], attrs={
                'class': 'w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500'
            }),
            'late_policy': forms.RadioSelect(attrs={
                'class': 'mt-1 border-slate-300 text-blue-600 focus:ring-blue-500'
            }),
            'published': forms.CheckboxInput(attrs={
                'class': 'hidden'
            })
        }

    def __init__(self, *args, **kwargs):
        faculty = kwargs.pop('faculty', None)
        super().__init__(*args, **kwargs)
        if faculty:
            self.fields['course'].queryset = Course.objects.filter(faculty=faculty, is_archived=False)
            # Batches query is more complex as it depends on courses, but for initial load:
            self.fields['batch'].queryset = Batch.objects.filter(courses__faculty=faculty, is_archived=False).distinct()
