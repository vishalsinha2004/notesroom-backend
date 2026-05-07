from django.contrib import admin
from .models import Document, Semester, Subject

# -- INLINES --
# These allow you to add child items directly from the parent's page

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1  # Shows one empty row by default to quickly upload a file
    fields = ('title', 'file', 'owner')
    
class SubjectInline(admin.TabularInline):
    model = Subject
    extra = 1
    fields = ('name',)

# -- MAIN ADMIN VIEWS --

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [SubjectInline] # Add Subjects directly while viewing a Semester

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'semester')
    list_filter = ('semester',)
    search_fields = ('name', 'semester__name')
    inlines = [DocumentInline] # Upload Documents directly while viewing a Subject

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    # This gives you a master list of all files across all folders
    list_display = ('title', 'subject', 'get_semester', 'uploaded_at', 'owner')
    list_filter = ('subject__semester', 'subject', 'uploaded_at')
    search_fields = ('title', 'subject__name')
    readonly_fields = ('uploaded_at',)

    # Display the parent semester in the document list
    def get_semester(self, obj):
        return obj.subject.semester.name
    get_semester.short_description = 'Semester'
    
    # Automatically assign the logged-in admin as the owner when uploading directly here
    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.owner:
            obj.owner = request.user
        super().save_model(request, obj, form, change)