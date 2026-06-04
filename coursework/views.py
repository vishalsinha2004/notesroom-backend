from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Semester, Document
from .serializers import SemesterSerializer, DocumentUploadSerializer

class SemesterViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny] 
    queryset = Semester.objects.all().order_by('name')
    serializer_class = SemesterSerializer

class DocumentUploadView(generics.CreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentUploadSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser] 

    def perform_create(self, serializer):
        # THIS IS THE FIX: It explicitly assigns the logged-in user as the owner!
        serializer.save(owner=self.request.user)