import random
import requests
import os
from django.core.mail import send_mail
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from .models import ExporterAccount, ExporterDetails

def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            return JsonResponse({'status': 'error', 'message': 'Email and password are required.'})

        if User.objects.filter(username=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email already registered. Please login.'})
            
        otp = str(random.randint(100000, 999999))
        
        request.session['signup_email'] = email
        request.session['signup_password'] = password
        request.session['signup_otp'] = otp
        request.session['signup_otp_time'] = timezone.now().timestamp()
        
        try:
            send_mail(
                subject='Your Exporter Account Verification Code',
                message=f'Your 6-digit verification code is: {otp}\n\nThis code will expire in 5 minutes.',
                from_email=None,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Failed to send verification email. Please try again later.'})
        
        return JsonResponse({'status': 'success', 'redirect': '/exporter/verify-otp/'})
        
    return render(request, 'exporter/signup.html')

def verify_otp_view(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        
        email = request.session.get('signup_email')
        password = request.session.get('signup_password')
        session_otp = request.session.get('signup_otp')
        otp_time = request.session.get('signup_otp_time')
        
        if not all([email, password, session_otp, otp_time]):
            return JsonResponse({'status': 'error', 'message': 'Session expired. Please sign up again.'})
            
        current_time = timezone.now().timestamp()
        if current_time - float(otp_time) > 300:
            return JsonResponse({'status': 'error', 'message': 'OTP expired. Please sign up again.'})
            
        if str(otp_entered) != str(session_otp):
            return JsonResponse({'status': 'error', 'message': 'Invalid OTP.'})
            
        if not User.objects.filter(username=email).exists():
            user = User.objects.create_user(username=email, email=email, password=password)
            ExporterAccount.objects.create(user=user, business_email=email, is_domain_verified=False)
            
            del request.session['signup_email']
            del request.session['signup_password']
            del request.session['signup_otp']
            del request.session['signup_otp_time']
            
            auth_login(request, user)
            
            return JsonResponse({'status': 'success', 'redirect': '/exporter/onboarding/'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Account already exists.'})
            
    return render(request, 'exporter/verify_otp.html')

def resend_otp_view(request):
    if request.method == 'POST':
        email = request.session.get('signup_email')
        
        if not email:
            return JsonResponse({'status': 'error', 'message': 'Session expired. Please sign up again.'})
            
        otp = str(random.randint(100000, 999999))
        
        request.session['signup_otp'] = otp
        request.session['signup_otp_time'] = timezone.now().timestamp()
        
        try:
            send_mail(
                subject='Your Exporter Account Verification Code (Resent)',
                message=f'Your new 6-digit verification code is: {otp}\n\nThis code will expire in 5 minutes.',
                from_email=None,
                recipient_list=[email],
                fail_silently=False,
            )
            return JsonResponse({'status': 'success', 'message': 'A new OTP has been sent to your email.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Failed to send verification email. Please try again later.'})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('exporter:onboarding')
        else:
            return render(request, 'exporter/login.html', {'error': 'Invalid credentials'})
    return render(request, 'exporter/login.html')

from django.contrib.auth.decorators import login_required
from .forms import ExporterDetailsForm

@login_required
def exporter_dashboard_view(request):
    try:
        exporter_account = request.user.exporter_profile
    except ExporterAccount.DoesNotExist:
        # Fallback if somehow they logged in without an exporter profile
        return redirect('exporter:login')
        
    details, created = ExporterDetails.objects.get_or_create(account=exporter_account)
    
    if request.method == 'POST':
        print("DEBUG: Dashboard POST received")
        form = ExporterDetailsForm(request.POST, instance=details)
        if form.is_valid():
            print("DEBUG: Form is valid, saving...")
            form.save()
            
            # Trigger n8n Webhook for 'Find Buyers'
            webhook_url = os.environ.get('N8N_WEBHOOK_URL')
            print(f"DEBUG: Webhook URL: {webhook_url}")
            if webhook_url:
                payload = {
                    'exporter_id': str(exporter_account.exporter_id),
                    'company_name': details.company_name or "",
                    'product_category': details.industry or "",
                    'target_market': details.target_region or "",
                    'email': exporter_account.business_email,
                    'timestamp': timezone.now().isoformat()
                }
                print(f"DEBUG: Sending payload to n8n: {payload}")
                try:
                    # We send it as an async-like request (short timeout) so it doesn't hang the UI
                    response = requests.post(webhook_url, json=payload, timeout=15)
                    print(f"DEBUG: n8n Webhook Status: {response.status_code}")
                    print(f"DEBUG: n8n Response: {response.text}")
                except Exception as e:
                    print(f"DEBUG: n8n Webhook failed: {e}")
            else:
                print("DEBUG: No Webhook URL found in environment!")
            
            return redirect('exporter:dashboard')
        else:
            print(f"DEBUG: Form errors: {form.errors}")
    else:
        form = ExporterDetailsForm(instance=details)
        
    return render(request, 'exporter/dashboard.html', {
        'form': form,
        'details': details,
        'account': exporter_account
    })

def onboarding(request):
    return render(request, 'exporter/onboarding.html')
