from django import forms
from main.models import CRMSettings, CustomerTier

class CRMSettingsForm(forms.ModelForm):
    class Meta:
        model = CRMSettings
        fields = ['points_per_currency', 'redemption_rate']
        widgets = {
            'points_per_currency': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'redemption_rate': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
        }

class CustomerTierForm(forms.ModelForm):
    class Meta:
        model = CustomerTier
        fields = ['name', 'min_spend', 'discount_percentage', 'color', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Gold'}),
            'min_spend': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'color': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. gold, blue, red'}),
            'icon': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. star, crown'}),
        }
