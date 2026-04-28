from django.urls import path
from . import views

app_name = 'exporter'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
    path('dashboard/', views.exporter_dashboard_view, name='dashboard'),
    path('onboarding/', views.onboarding, name='onboarding'),
]
