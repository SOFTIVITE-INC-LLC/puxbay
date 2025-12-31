from django import forms
from django.forms import inlineformset_factory
from .models import (
    ExpenseCategory, Expense, TaxConfiguration, 
    PaymentMethod, Return, ReturnItem, Order
)

class ExpenseCategoryForm(forms.ModelForm):
    """Form for creating/editing expense categories"""
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'type', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'e.g., Rent, Utilities, Salaries'
            }),
            'type': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Optional description'
            }),
        }

class ExpenseForm(forms.ModelForm):
    """Form for recording expenses"""
    class Meta:
        model = Expense
        fields = ['category', 'branch', 'amount', 'date', 'description', 'receipt_file']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'branch': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 4,
                'placeholder': 'Describe the expense...'
            }),
            'receipt_file': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'accept': 'image/*,.pdf'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        
        if tenant:
            self.fields['category'].queryset = ExpenseCategory.objects.filter(tenant=tenant)
            self.fields['branch'].queryset = tenant.branches.all()
            self.fields['branch'].required = False
            self.fields['branch'].empty_label = "Company-wide"

class TaxConfigurationForm(forms.ModelForm):
    """Form for configuring tax settings"""
    class Meta:
        model = TaxConfiguration
        fields = ['tax_type', 'tax_rate', 'tax_number', 'include_tax_in_prices', 'is_active']
        widgets = {
            'tax_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': '15.00',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'tax_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Tax registration number'
            }),
            'include_tax_in_prices': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-2 focus:ring-blue-500'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-2 focus:ring-blue-500'
            }),
        }

class PaymentMethodForm(forms.ModelForm):
    """Form for configuring payment gateways"""
    class Meta:
        model = PaymentMethod
        fields = ['name', 'provider', 'is_active', 'api_key_hint']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'e.g., Stripe Payment'
            }),
            'provider': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-2 focus:ring-blue-500'
            }),
            'api_key_hint': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Last 4 characters of API key',
                'maxlength': '50'
            }),
        }

class ReturnForm(forms.ModelForm):
    """Form for creating return requests"""
    order_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Enter order ID to search'
        })
    )
    
    class Meta:
        model = Return
        fields = ['order', 'customer', 'reason', 'reason_detail', 'refund_method', 'restocking_fee']
        widgets = {
            'order': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'customer': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'reason': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'refund_method': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'restocking_fee': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        branch = kwargs.pop('branch', None)
        super().__init__(*args, **kwargs)
        
        if tenant:
            if branch:
                self.fields['order'].queryset = Order.objects.filter(tenant=tenant, branch=branch, status='completed')
            else:
                self.fields['order'].queryset = Order.objects.filter(tenant=tenant, status='completed')
            self.fields['customer'].queryset = tenant.customers.all()

class ReturnItemForm(forms.ModelForm):
    """Form for individual items in a return"""
    class Meta:
        model = ReturnItem
        fields = ['product', 'quantity', 'condition', 'restock']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'min': '1'
            }),
            'condition': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'restock': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-2 focus:ring-blue-500'
            }),
        }

class BaseReturnItemFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.order = kwargs.pop('order', None)
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        form = super()._construct_form(i, **kwargs)
        if self.order:
            # Filter products to only those in the original order
            from .models import OrderItem, Product
            product_ids = OrderItem.objects.filter(order=self.order).values_list('product_id', flat=True)
            form.fields['product'].queryset = Product.objects.filter(id__in=product_ids)
        return form

# Formset for managing multiple return items
ReturnItemFormSet = inlineformset_factory(
    Return,
    ReturnItem,
    form=ReturnItemForm,
    formset=BaseReturnItemFormSet,
    extra=1,
    can_delete=True
)
