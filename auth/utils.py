# utils.py - Email verification utilities
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

def send_verification_email(user, verification_token):
    verification_url = f"{settings.SITE_URL}{reverse('verify-email')}?token={verification_token}"
    
    subject = 'Verify your email address'
    message = f'''
    Hello {user.username},
    
    Thank you for registering with our loan management system.
    Please verify your email address by clicking on the link below:
    
    {verification_url}
    
    This link will expire in 24 hours.
    
    Best regards,
    Loan Management Team
    '''
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )