from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('', login_required(views.UserProfile.as_view()), name='user-profile'),
    path('login/', views.UserLogin.as_view(), name='login'),
    path('register/', views.UserRegister.as_view(), name='register'),
    path('logout/', views.UserLogout.as_view(), name='logout'),
    path('verify/<uidb64>/<token>/', views.UserVerifyEmail.as_view(), name='verify-email'),
    path('pwd/forgot/', views.UserForgotPwd.as_view(), name='pwd-forgot'),
    path('pwd/reset/<uidb64>/<token>/', views.UserResetPwd.as_view(), name='pwd-reset')
]