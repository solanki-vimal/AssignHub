from django.db import models
from django.conf import settings
from academic.models import Course, Batch

class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='assignments')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'faculty'},
        related_name='created_assignments'
    )
    due_date = models.DateTimeField()
    
    # Prototype Alignment Fields
    start_date = models.DateTimeField(null=True, blank=True)
    max_marks = models.IntegerField(default=100)
    allowed_file_types = models.CharField(max_length=255, default='all', help_text="Comma separated types, e.g., 'pdf,docx,jpg'")
    max_file_size_mb = models.IntegerField(default=10)
    LATE_POLICY_CHOICES = [
        ('strict', 'Strict Deadline'),
        ('allow_penalty', 'Allow Late Submissions')
    ]
    late_policy = models.CharField(max_length=50, choices=LATE_POLICY_CHOICES, default='allow_penalty')
    
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class AssignmentAttachment(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='assignments/attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.assignment.title}"

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='submissions'
    )
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('late', 'Late Submission'),
        ('evaluated', 'Evaluated')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Evaluation fields
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    faculty_remarks = models.TextField(blank=True)
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

def submission_file_path(instance, filename):
    """Store files in a structured path: submissions/assignment_{id}/student_{id}/filename"""
    return f"submissions/assignment_{instance.submission.assignment_id}/student_{instance.submission.student_id}/{filename}"

class SubmissionFile(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=submission_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.submission}"
