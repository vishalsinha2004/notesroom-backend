from rest_framework import viewsets
from rest_framework.permissions import AllowAny # <-- 1. Import AllowAny
from .models import Semester
from .serializers import SemesterSerializer

# Use ReadOnlyModelViewSet so users can fetch but NOT create/update/delete
class SemesterViewSet(viewsets.ReadOnlyModelViewSet):
    # 2. Change permission to AllowAny so guests can see the folders on the home page
    permission_classes = [AllowAny] 
    
    queryset = Semester.objects.all().order_by('name')
    serializer_class = SemesterSerializer