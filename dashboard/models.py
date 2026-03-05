from django.db import models
from django.conf import settings

class ActivityLog(models.Model):
    ACTION_CHOICES = (
        ('auth', 'Auth'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    action_name = models.CharField(max_length=100) # e.g. "User Login", "Assignment Created"
    details = models.TextField() # e.g. "Lab 3: UML Diagrams" or IP address
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action_name} at {self.timestamp}"

class SystemSettings(models.Model):
    institution_name = models.CharField(max_length=200, default="Dharmsinh Desai University")
    system_email = models.EmailField(default="assignhub@ddu.ac.in")
    current_academic_year = models.CharField(max_length=20, default="2024-25")
    current_semester = models.CharField(max_length=50, default="Even (Jan-Jun)")
    maintenance_mode = models.BooleanField(default=False)
    
    max_file_size_mb = models.IntegerField(default=10)
    allowed_formats = models.CharField(max_length=200, default="PDF, DOCX, ZIP")
    allow_late_submissions = models.BooleanField(default=True)
    
    email_notifications = models.BooleanField(default=True)
    
    session_timeout_mins = models.IntegerField(default=60)
    max_login_attempts = models.IntegerField(default=5)
    require_2fa = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super(SystemSettings, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "System Settings"
