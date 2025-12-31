
from django import forms
from django.forms import inlineformset_factory
from .models import Product, Category, Customer, GiftCard, ProductComponent, Supplier, FeedbackReport
from branches.models_workforce import CommissionRule

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address', 'customer_type', 'loyalty_points', 'store_credit_balance', 'credit_limit', 'outstanding_debt']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'customer_type': forms.Select(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'credit_limit': forms.NumberInput(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'category', 'supplier', 'price', 
            'wholesale_price', 'minimum_wholesale_quantity',
            'cost_price', 'stock_quantity', 'low_stock_threshold',
            'barcode', 'expiry_date', 'batch_number', 'invoice_waybill_number',
            'country_of_origin', 'manufacturer_name', 'manufacturer_address', 'manufacturing_date',
            'image', 'description', 'is_active', 'is_composite'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'manufacturer_address': forms.Textarea(attrs={'rows': 2}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'manufacturing_date': forms.DateInput(attrs={'type': 'date'}),
            'image': forms.FileInput(attrs={'class': 'hidden', 'accept': 'image/*', 'id': 'product-image-input'}),
        }
        
class GiftCardForm(forms.ModelForm):
    class Meta:
        model = GiftCard
        fields = ['code', 'balance', 'expiry_date', 'status']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'balance': forms.NumberInput(attrs={'class': 'block w-full rounded-lg border-slate-300 pl-8 focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'status': forms.Select(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'status': forms.Select(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
        }

ProductComponentFormSet = inlineformset_factory(
    Product, 
    ProductComponent,
    fk_name='parent_product',
    fields=['component_product', 'quantity'],
    extra=1,
    can_delete=True,
    widgets={
        'component_product': forms.Select(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
        'quantity': forms.NumberInput(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm', 'min': '1'}),
    }
)

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address', 'tax_id', 'payment_terms', 'credit_limit', 'outstanding_balance', 'is_active']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'standard-input', 'placeholder': 'Global Office Address'}),
            'name': forms.TextInput(attrs={'class': 'standard-input', 'placeholder': 'Legal Company Name'}),
            'contact_person': forms.TextInput(attrs={'class': 'standard-input', 'placeholder': 'Contact Name'}),
            'email': forms.EmailInput(attrs={'class': 'standard-input', 'placeholder': 'email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'standard-input', 'placeholder': 'Phone Number'}),
            'tax_id': forms.TextInput(attrs={'class': 'standard-input', 'placeholder': 'Tax ID / VAT'}),
            'payment_terms': forms.TextInput(attrs={'class': 'standard-input', 'placeholder': 'e.g. Net 30'}),
            'credit_limit': forms.NumberInput(attrs={'class': 'standard-input', 'step': '0.01'}),
            'outstanding_balance': forms.NumberInput(attrs={'class': 'standard-input', 'step': '0.01'}),
        }

class CommissionRuleForm(forms.ModelForm):
    class Meta:
        model = CommissionRule
        fields = ['name', 'min_sales_amount', 'commission_percentage', 'flat_bonus', 'branch']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'min_sales_amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'commission_percentage': forms.NumberInput(attrs={'step': '0.01', 'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'flat_bonus': forms.NumberInput(attrs={'step': '0.01', 'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'branch': forms.Select(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = FeedbackReport
        fields = ['report_type', 'priority', 'subject', 'message']
        widgets = {
            'report_type': forms.Select(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'priority': forms.Select(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'subject': forms.TextInput(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm', 'placeholder': 'Brief summary of the issue'}),
            'message': forms.Textarea(attrs={'rows': 4, 'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm', 'placeholder': 'Describe your issue or suggestion in detail...'}),
        }
