"""
Models for the assignments app.

Defines the complete assignment lifecycle:
  Faculty creates Assignment → Student submits Submission → Faculty evaluates

Models:
  - Assignment: A lab task created by faculty, linked to a Course and Batch
  - AssignmentAttachment: Reference files uploaded by faculty
  - Submission: A student's response to an assignment
  - SubmissionFile: Files uploaded by students as part of their submission
"""

import os
from django.db import models
from django.conf import settings
from academic.models import Course, Batch


# =============================================================================
# Assignment (Created by Faculty)
# =============================================================================

class Assignment(models.Model):
    """
    Represents a lab assignment created by a faculty member.
    Only visible to students when published=True.
    """

    title = models.CharField(max_length=255)
    description = models.TextField()

    # Which course and batch this assignment belongs to
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='assignments')

    # The faculty who created this assignment
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'faculty'},  # Only faculty can create assignments
        related_name='created_assignments'
    )

    # Schedule & grading
    start_date = models.DateTimeField(null=True, blank=True)   # When the assignment becomes available
    due_date = models.DateTimeField()                           # Submission deadline
    max_marks = models.IntegerField(default=100)

    # File upload constraints for student submissions
    allowed_file_types = models.CharField(
        max_length=255, default='all',
        help_text="Comma separated types, e.g., 'pdf,docx,jpg'"
    )
    max_file_size_mb = models.IntegerField(default=10)

    # Late submission policy
    LATE_POLICY_CHOICES = [
        ('strict', 'Strict Deadline'),          # No submissions after due_date
        ('allow_penalty', 'Allow Late Submissions')  # Late submissions accepted
    ]
    late_policy = models.CharField(max_length=50, choices=LATE_POLICY_CHOICES, default='allow_penalty')

    # Draft/publish toggle — students only see published assignments
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =============================================================================
# Assignment Attachments (Faculty Reference Files)
# =============================================================================

def assignment_attachment_path(instance, filename):
    """Upload path: media/assignments/assignment_<id>/attachments/<filename>"""
    return f"assignments/assignment_{instance.assignment.id}/attachments/{filename}"


class AssignmentAttachment(models.Model):
    """Reference files attached to an assignment by faculty (e.g., problem statements, PDFs)."""

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=assignment_attachment_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.assignment.title}"


# =============================================================================
# Submission (Student Response)
# =============================================================================

class Submission(models.Model):
    """
    A student's submission for an assignment.
    Each student can only submit once per assignment (enforced by unique_together).
    Status flow: pending → submitted/late → evaluated
    """

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},  # Only students can submit
        related_name='submissions'
    )

    STATUS_CHOICES = [
        ('pending', 'Pending'),          # Assignment assigned but not yet submitted
        ('submitted', 'Submitted'),      # Submitted on time
        ('late', 'Late Submission'),     # Submitted after due_date
        ('evaluated', 'Evaluated')       # Graded by faculty
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Evaluation fields (filled by faculty during grading)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    faculty_remarks = models.TextField(blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('assignment', 'student')  # One submission per student per assignment

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"


# =============================================================================
# Submission Files (Student Uploaded Files)
# =============================================================================

def submission_file_path(instance, filename):
    """Upload path: media/submissions/assignment_<id>/student_<id>/<filename>"""
    return f"submissions/assignment_{instance.submission.assignment_id}/student_{instance.submission.student_id}/{filename}"


class SubmissionFile(models.Model):
    """Files uploaded by a student as part of their submission."""

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=submission_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.submission}"

    @property
    def filename(self):
        """Returns just the file name (without the full path)."""
        return os.path.basename(self.file.name)
