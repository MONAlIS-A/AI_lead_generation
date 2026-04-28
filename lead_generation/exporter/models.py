from django.db import models
from django.contrib.auth.models import User
import uuid

class ExporterAccount(models.Model):
    exporter_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='exporter_profile')
    business_email = models.EmailField(unique=True)
    main_domain = models.CharField(max_length=255, blank=True, null=True)
    is_domain_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.business_email

class ExporterDetails(models.Model):
    # Link to the main ExporterAccount
    account = models.OneToOneField(ExporterAccount, on_delete=models.CASCADE, related_name='details')
    
    # Company Details
    company_name = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True)
    
    # Product Information
    product_list_sku = models.TextField(blank=True, null=True, help_text="Product List (SKU)")
    product_description = models.TextField(blank=True, null=True)
    
    # Target Market
    target_region = models.CharField(max_length=255, blank=True, null=True, help_text="Region / Country")
    buyer_type = models.CharField(max_length=255, blank=True, null=True)
    
    # Outreach Preferences
    preferred_channel = models.CharField(max_length=255, blank=True, null=True, help_text="E.g., Email, LinkedIn, WhatsApp")
    language_preference = models.CharField(max_length=100, blank=True, null=True)
    
    # Technical Setup Extra (Email/Domain is from ExporterAccount)
    spf_verified = models.BooleanField(default=False)
    dkim_verified = models.BooleanField(default=False)
    dmarc_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Details for {self.account.business_email}"
