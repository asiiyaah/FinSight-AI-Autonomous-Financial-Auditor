from django.urls import path
from chatbot.views import StatementChatView

urlpatterns = [
    path(
        "statements/<int:statement_id>/chat/",
        StatementChatView.as_view(),
        name="statement-chat",
    ),
]