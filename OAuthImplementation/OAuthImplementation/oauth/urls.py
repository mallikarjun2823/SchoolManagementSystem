from django.urls import path
from . import views

app_name = 'oauth'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/google/', views.google_login, name='login'),
    path('callback/google/', views.google_callback, name='callback'),
    path('profile/', views.profile, name='profile'),
    path('api/profile/', views.profile_api, name='profile_api'),
    path('logout/', views.logout_view, name='logout'),
]
