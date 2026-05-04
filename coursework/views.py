from rest_framework import viewsets
from .models import Document
from .serializers import DocumentSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    # CORRECTED LINE: Using .order_by() instead of the accidental equals sign
    queryset = Document.objects.all().order_by('-uploaded_at')
    serializer_class = DocumentSerializer