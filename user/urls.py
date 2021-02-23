from django.urls import path

from . import views

urlpatterns = [
    path('', views.UserProfile.as_view(), name='user-profile'),
    path('login/', views.UserLogin.as_view(), name='login'),
    path('register/', views.UserRegister.as_view(), name='register'),
    path('logout/', views.UserLogout.as_view(), name='logout'),
    path('verify/<uidb64>/<token>', views.UserVerifyEmail.as_view(), name='verify-email'),
]