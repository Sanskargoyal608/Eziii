# core/urls.py

from django.urls import path
from .views import DocumentListView
from .views import FederatedQueryView , StudentListView , RegisterView , LoginView

urlpatterns = [

    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),

    
    path('students/', StudentListView.as_view(), name='student-list'),
    path('documents/', DocumentListView.as_view(), name='document-list'),

    path('federated-query/', FederatedQueryView.as_view(), name='federated-query'),
]
