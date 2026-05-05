from django.db import models
from django.contrib.auth.models import User # 1. Import the User model

class Document(models.Model):
    # 2. Add the owner field
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    
    title = models.CharField(max_length=255)
    semester = models.CharField(max_length=50, help_text="e.g., Semester_4")
    subject = models.CharField(max_length=100, help_text="e.g., IOS")
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.title}"