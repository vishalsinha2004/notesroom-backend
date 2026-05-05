from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Document
from .serializers import DocumentSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentSerializer

    # 1. Only return documents owned by the logged-in user
    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user).order_by('-uploaded_at')

    # 2. Automatically assign the logged-in user as the owner when uploading
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)