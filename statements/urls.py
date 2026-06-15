from django.urls import path
from .views import StatementUploadView,StatementAuditView


urlpatterns = [
    path('upload/',StatementUploadView.as_view(),name='upload'),
    path('<int:statement_id>/audit/',StatementAuditView.as_view(),name='audit'),
]