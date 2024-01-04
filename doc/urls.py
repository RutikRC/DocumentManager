from django.urls import path
from . views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('client/', ClientListView.as_view(), name='client-list'),
    path('client/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
    path('job/', JobListView.as_view(), name='job-list'),
    path('job/<int:pk>/', JobDetailView.as_view(), name='job-detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
