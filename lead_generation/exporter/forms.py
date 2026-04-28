from django import forms
from .models import ExporterDetails, ExporterAccount

class ExporterDetailsForm(forms.ModelForm):
    class Meta:
        model = ExporterDetails
        fields = [
            'company_name', 'industry', 'product_list_sku', 
            'product_description', 'target_region', 'buyer_type',
            'preferred_channel', 'language_preference'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Industry / Category'}),
            'product_list_sku': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Product List (SKU)'}),
            'product_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Product Description'}),
            'target_region': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Region / Country'}),
            'buyer_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buyer Type'}),
            'preferred_channel': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Email, LinkedIn, WhatsApp'}),
            'language_preference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Language Preference'}),
        }
