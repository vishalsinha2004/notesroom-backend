from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Semester
from .serializers import SemesterSerializer

# Use ReadOnlyModelViewSet so users can fetch but NOT create/update/delete
class SemesterViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Semester.objects.all().order_by('name')
    serializer_class = SemesterSerializer