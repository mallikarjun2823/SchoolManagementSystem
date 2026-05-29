"""URL routes for accounts API endpoints.

Provides routes for user registration, authentication and token
refreshing.
"""

from django.urls import path

from .views import LoginView, RegistrationView, RefreshView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', RefreshView.as_view(), name='token_refresh'),
]