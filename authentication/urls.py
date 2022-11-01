from django.urls import path
from .views import (
    SignupView, 
    LoginView, 
    VerifyEmail, 
    RequestPasswordResetEmail, 
    PasswordTokenCheckAPI,
    SetNewPasswordAPIView
    )

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-email/', VerifyEmail.as_view(), name='verify-email'),
    path('request-reset-password-email/', RequestPasswordResetEmail.as_view(),
         name='request-reset-password-email'),
    path('password-reset/<uid64>/<token>/',
         PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('set-new-password/', SetNewPasswordAPIView.as_view(),
         name='set-new-password')
]
