from django import forms
from .models import CustomerCreditTransaction, SupplierCreditTransaction

class CustomerPaymentForm(forms.ModelForm):
    class Meta:
        model = CustomerCreditTransaction
        fields = ['amount', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'block w-full px-4 py-3 rounded-xl border-slate-200 focus:border-blue-500 focus:ring-blue-500 transition-colors',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-3 rounded-xl border-slate-200 focus:border-blue-500 focus:ring-blue-500 transition-colors',
                'placeholder': 'Add payment notes (e.g., Receipt #, check info...)',
                'rows': 3
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Payment amount must be greater than zero.")
        return amount

class SupplierPaymentForm(forms.ModelForm):
    class Meta:
        model = SupplierCreditTransaction
        fields = ['amount', 'receipt_image', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'block w-full px-4 py-3 rounded-xl border-slate-200 focus:border-blue-500 focus:ring-blue-500 transition-colors',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-3 rounded-xl border-slate-200 focus:border-blue-500 focus:ring-blue-500 transition-colors',
                'placeholder': 'Add payment notes...',
                'rows': 3
            }),
            'receipt_image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition-all'
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Payment amount must be greater than zero.")
        return amount
    
    def clean_receipt_image(self):
        receipt = self.cleaned_data.get('receipt_image')
        if not receipt:
            raise forms.ValidationError("A receipt image is required for supplier payments.")
        return receipt
