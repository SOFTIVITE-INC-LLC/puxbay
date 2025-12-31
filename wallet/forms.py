from django import forms

class WalletLoginForm(forms.Form):
    phone = forms.CharField(
        max_length=20, 
        widget=forms.TextInput(attrs={
            'class': 'w-full px-5 py-4 rounded-2xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all font-medium',
            'placeholder': 'Enter your phone number',
            'type': 'tel'
        })
    )
