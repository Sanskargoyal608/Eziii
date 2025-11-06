# core/urls.py

from django.urls import path
from .views import DocumentListView
from .views import FederatedQueryView , StudentListView , RegisterView , LoginView , DocumentUploadView , GeneratePDFView , AdminDashboardView , StudentSummaryView , AdminChatView

urlpatterns = [

    path('dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('summary/<int:student_id>/', StudentSummaryView.as_view(), name='admin-student-summary'),
    path('chat/', AdminChatView.as_view(), name='admin-chat'),

    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),

    
    path('students/', StudentListView.as_view(), name='student-list'),
    path('documents/', DocumentListView.as_view(), name='document-list'),

    path('federated-query/', FederatedQueryView.as_view(), name='federated-query'),

    path('documents/upload/', DocumentUploadView.as_view(), name='document-upload'),

    path('generate-pdf/', GeneratePDFView.as_view(), name='generate-pdf'),
]
