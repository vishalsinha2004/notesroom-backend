from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import send_new_document_notification

# 1. New Folder Structure Models
class Semester(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="e.g., Semester 4")

    def __str__(self):
        return self.name

class Subject(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=100, help_text="e.g., iOS Development")

    def __str__(self):
        return f"{self.name} ({self.semester.name})"

class Document(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Owner is the admin who uploads it
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')

    def __str__(self):
        return f"{self.title} - {self.subject.name}"

# 2. Your Existing OTP Model
class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # Code expires after 10 minutes (600 seconds)
        return (timezone.now() - self.created_at).total_seconds() < 600
    
@receiver(post_save, sender=Document)
def trigger_document_notification(sender, instance, created, **kwargs):
    # 'created' is a boolean that is True ONLY when the document is first uploaded.
    # This prevents sending emails again if you simply edit or rename the file later!
    if created:
        try:
            send_new_document_notification(instance)
        except Exception as e:
            print(f"Failed to trigger email thread: {e}")