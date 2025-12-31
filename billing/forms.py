from django import forms

class PaymentProviderForm(forms.Form):
    PROVIDER_CHOICES = (
        ('stripe', 'Stripe'),
        ('paystack', 'Paystack'),
        ('paypal', 'PayPal'),
    )
    payment_provider = forms.ChoiceField(choices=PROVIDER_CHOICES, widget=forms.RadioSelect())
