from django.contrib import admin
from django.urls import path
from OAuthImplementation.oauth import views as oauth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', oauth_views.home, name='home'),
    path('login/google/', oauth_views.google_login, name='login'),
    path('google/callback', oauth_views.google_callback, name='callback'),
    path('profile/', oauth_views.profile, name='profile'),
    path('api/profile/', oauth_views.profile_api, name='profile_api'),
    path('logout/', oauth_views.logout_view, name='logout'),

    path('auth/', oauth_views.home, name='auth_home'),
    path('auth/login/google/', oauth_views.google_login, name='auth_login'),
    path('auth/google/callback', oauth_views.google_callback, name='auth_callback'),
    path('auth/profile/', oauth_views.profile, name='auth_profile'),
    path('auth/api/profile/', oauth_views.profile_api, name='auth_profile_api'),
    path('auth/logout/', oauth_views.logout_view, name='auth_logout'),
]
