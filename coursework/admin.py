from django.contrib import admin
from .models import Document, Semester, Subject

# -- INLINES --
# These allow you to add child items directly from the parent's page

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1  # Shows one empty row by default to quickly upload a file
    fields = ('title', 'file', 'notify_users', 'owner')
    # Optional but recommended: make owner readonly in the inline so it automatically fills
    readonly_fields = ('owner',)
    
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

    # NEW FIX: This catches documents uploaded via the Inline on the Subject page
    # and automatically sets the logged-in admin as the owner.
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            # Check if the instance being saved is a Document and has no owner
            if isinstance(instance, Document) and not instance.owner:
                instance.owner = request.user
            instance.save()
        formset.save_m2m()


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'get_semester', 'uploaded_at', 'notify_users', 'owner')
    list_filter = ('subject__semester', 'subject', 'notify_users', 'uploaded_at')
    search_fields = ('title', 'subject__name')
    readonly_fields = ('uploaded_at', 'owner') # Made owner readonly so it just auto-fills

    # Display the parent semester in the document list
    def get_semester(self, obj):
        return obj.subject.semester.name
    get_semester.short_description = 'Semester'
    
    # This catches documents uploaded directly on the main Document page
    def save_model(self, request, obj, form, change):
        # Always set the owner to the user uploading it if it's not set
        if not obj.owner:
            obj.owner = request.user
        super().save_model(request, obj, form, change)