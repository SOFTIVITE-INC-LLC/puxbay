from django import forms
from main.models import CustomerFeedback

class CustomerFeedbackForm(forms.ModelForm):
    # Extra fields for identification since public users aren't logged in
    name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your Name'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Your Email'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your Phone'}))

    class Meta:
        model = CustomerFeedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Tell us about your experience...'}),
        }
