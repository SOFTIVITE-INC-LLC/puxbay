from django import forms
from accounts.models import Branch, UserProfile
from main.models import Product
from .models import Shift, CashDrawerSession
from accounts.models import Branch

class BranchSettingsForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['logo', 'low_stock_threshold', 'currency_symbol', 'currency_code', 'receipt_header', 'receipt_footer']
        widgets = {
            'logo': forms.FileInput(attrs={'class': 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition-colors'}),
            'low_stock_threshold': forms.NumberInput(attrs={'class': 'block w-full rounded-md border-0 px-3 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6'}),
            'currency_symbol': forms.TextInput(attrs={'class': 'block w-full rounded-md border-0 px-3 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6'}),
            'currency_code': forms.Select(attrs={'class': 'block w-full rounded-md border-0 px-3 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6'}),
            'receipt_header': forms.Textarea(attrs={'rows': 3, 'class': 'block w-full rounded-md border-0 px-3 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6'}),
            'receipt_footer': forms.Textarea(attrs={'rows': 3, 'class': 'block w-full rounded-md border-0 px-3 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6'}),
        }

class ProductImportForm(forms.Form):
    import_file = forms.FileField(
        label='File',
        help_text='Upload a valid .xlsx or .csv file.',
        widget=forms.FileInput(attrs={
            'class': 'absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10',
            'accept': '.xlsx,.csv'
        })
    )

class StockAdjustmentForm(forms.Form):
    ADJUSTMENT_TYPES = (
        ('add', 'Add Stock'),
        ('remove', 'Remove Stock'),
        ('set', 'Set Absolute Quantity'),
    )
    product = forms.ModelChoiceField(queryset=Product.objects.none(), widget=forms.Select(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}))
    adjustment_type = forms.ChoiceField(choices=ADJUSTMENT_TYPES, widget=forms.Select(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}))
    quantity = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2, 'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}))

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['product'].queryset = Product.objects.filter(tenant=tenant)

class ShiftAssignmentForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['staff', 'start_time', 'end_time', 'role', 'notes']
        widgets = {
            'staff': forms.Select(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'role': forms.Select(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
        }

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['staff'].queryset = UserProfile.objects.filter(tenant=tenant)

class CashSessionForm(forms.ModelForm):
    class Meta:
        model = CashDrawerSession
        fields = ['starting_balance', 'notes']
        widgets = {
            'starting_balance': forms.NumberInput(attrs={'step': '0.01', 'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
        }

class CashDrawerCloseForm(forms.ModelForm):
    class Meta:
        model = CashDrawerSession
        fields = ['actual_cash', 'notes']
        widgets = {
            'actual_cash': forms.NumberInput(attrs={'step': '0.01', 'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
        }

class StockReceiveForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.none(), widget=forms.Select(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}))
    batch_number = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}))
    expiry_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}))
    quantity = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}))
    cost_price = forms.DecimalField(max_digits=15, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}))

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        branch = kwargs.pop('branch', None)
        super().__init__(*args, **kwargs)
        if tenant and branch:
            self.fields['product'].queryset = Product.objects.filter(tenant=tenant, branch=branch)
