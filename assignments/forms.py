from django import forms
from .models import Assignment
from academic.models import Course, Batch

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'course', 'batch', 'due_date', 'published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all',
                'placeholder': 'e.g. Lab 1: Getting Started'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all resize-none',
                'rows': 5,
                'placeholder': 'Enter assignment instructions...'
            }),
            'course': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all'
            }),
            'batch': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all'
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all text-slate-600',
                'type': 'datetime-local'
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
