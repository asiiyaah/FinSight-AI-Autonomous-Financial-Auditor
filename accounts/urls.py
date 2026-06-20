from django.urls import path
from .views import RegisterView,signup_page,MeView,EmailLoginView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns=[
    path('register/',RegisterView.as_view(),name='register'),
    path('signup/', signup_page, name='signup_html_screen'),
    # The login endpoint to get your tokens
    path('login/', EmailLoginView.as_view(), name='login'),
    # The endpoint to get a new access token using a refresh token
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/',MeView.as_view(),name='me')
]
