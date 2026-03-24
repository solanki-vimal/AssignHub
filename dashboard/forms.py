from django import forms
from assignments.models import Submission
from academic.models import Course

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
