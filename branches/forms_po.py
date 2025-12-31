from django import forms
from .models import Supplier, PurchaseOrder
from main.models import Product

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address']

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'expected_date', 'notes', 'amount_paid', 'payment_method']
        widgets = {
            'expected_date': forms.DateInput(attrs={'type': 'date', 'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'supplier': forms.Select(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
        }
    
    amount_paid = forms.DecimalField(required=False, initial=0.00, widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}))
    payment_method = forms.ChoiceField(choices=[('cash', 'Cash'), ('card', 'Card'), ('bank', 'Bank Transfer')], required=False, initial='cash', widget=forms.Select(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}))
    
    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super(PurchaseOrderForm, self).__init__(*args, **kwargs)
        if self.tenant:
            self.fields['supplier'].queryset = Supplier.objects.filter(tenant=self.tenant)
