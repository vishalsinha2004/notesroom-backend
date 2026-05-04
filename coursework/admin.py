from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'semester', 'uploaded_at')
    list_filter = ('semester', 'subject')
    search_fields = ('title', 'subject')