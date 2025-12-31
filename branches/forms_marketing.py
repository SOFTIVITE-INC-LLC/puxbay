from django import forms
from main.models import MarketingCampaign

class MarketingCampaignForm(forms.ModelForm):
    class Meta:
        model = MarketingCampaign
        fields = ['name', 'campaign_type', 'subject', 'message', 'target_tier', 'is_automated', 'trigger_event', 'scheduled_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Internal Campaign Name'}),
            'campaign_type': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Email Subject / SMS Header'}),
            'message': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 5, 'placeholder': 'Write your message here...'}),
            'target_tier': forms.Select(attrs={'class': 'form-select'}),
            'is_automated': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500'}),
            'trigger_event': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_at': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
        }
