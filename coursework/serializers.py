from rest_framework import serializers
from .models import Document, Semester, Subject

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'uploaded_at']

class SubjectSerializer(serializers.ModelSerializer):
    # This nests the documents inside their respective subject
    documents = DocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'documents']

class SemesterSerializer(serializers.ModelSerializer):
    # This nests the subjects inside their respective semester
    subjects = SubjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = Semester
        fields = ['id', 'name', 'subjects']