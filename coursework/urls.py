from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SemesterViewSet, DocumentUploadView

router = DefaultRouter()
router.register(r'semesters', SemesterViewSet, basename='semester')

urlpatterns = [
    path('', include(router.urls)),
    path('upload-document/', DocumentUploadView.as_view(), name='upload-document'), # ADD THIS LINE
]