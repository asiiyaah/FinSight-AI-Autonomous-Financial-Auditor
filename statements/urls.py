from django.urls import path
from .views import StatementUploadView,StatementAuditView,StatementListView,StatementDetailView


urlpatterns = [
    path('',StatementListView.as_view(), name='statement-list'),
    path('<int:statement_id>/',StatementDetailView.as_view(),name='statement-details'),
    path('upload/',StatementUploadView.as_view(),name='upload'),
    path('<int:statement_id>/audit/',StatementAuditView.as_view(),name='audit'),
]