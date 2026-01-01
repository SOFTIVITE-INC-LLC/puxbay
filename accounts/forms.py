from django import forms
from django.contrib.auth.models import User
from .models import Tenant, Branch, APIKey

class TenantRegistrationForm(forms.ModelForm):
    name = forms.CharField(label="Company Name", max_length=100)
    subdomain = forms.CharField(label="Subdomain (e.g., storename)", max_length=100, help_text="Lowercase letters only, no numbers, spaces or special characters.")
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = Tenant
        fields = ['name', 'subdomain', 'address']

    def clean_subdomain(self):
        subdomain = self.cleaned_data.get('subdomain')
        if Tenant.objects.filter(subdomain=subdomain).exists():
            raise forms.ValidationError("This subdomain is already taken. Please choose another one.")
        return subdomain

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'address', 'phone', 'branch_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ring-1 ring-slate-200 sm:text-sm h-10 px-3 transition-all'}),
            'address': forms.Textarea(attrs={'rows': 4, 'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ring-1 ring-slate-200 sm:text-sm p-2.5 transition-all'}),
            'phone': forms.TextInput(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ring-1 ring-slate-200 sm:text-sm h-10 px-3 transition-all'}),
            'branch_type': forms.Select(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ring-1 ring-slate-200 sm:text-sm h-10 px-3 transition-all'}),
        }
class StaffCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ring-1 ring-slate-200 sm:text-sm h-10 px-3 transition-all'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ring-1 ring-slate-200 sm:text-sm h-10 px-3 transition-all'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ring-1 ring-slate-200 sm:text-sm h-10 px-3 transition-all'}))
    role = forms.ChoiceField(choices=[
        ('manager', 'Branch Manager'),
        ('procurement_manager', 'Procurement Manager'),
        ('sales', 'Sales Person'),
        ('financial', 'Financial'),
    ], widget=forms.Select(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ring-1 ring-slate-200 sm:text-sm h-10 px-3 transition-all'}))
    branch = forms.ModelChoiceField(queryset=Branch.objects.none(), widget=forms.Select(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ring-1 ring-slate-200 sm:text-sm h-10 px-3 transition-all'}))
    can_perform_credit_sales = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'h-5 w-5 rounded border-slate-300 text-blue-600 focus:ring-blue-500'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['branch'].queryset = Branch.objects.filter(tenant=tenant)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class StaffUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ring-1 ring-slate-200 sm:text-sm h-10 px-3 transition-all'}))
    role = forms.ChoiceField(choices=[
        ('manager', 'Branch Manager'),
        ('procurement_manager', 'Procurement Manager'),
        ('sales', 'Sales Person'),
        ('financial', 'Financial'),
    ], widget=forms.Select(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ring-1 ring-slate-200 sm:text-sm h-10 px-3 transition-all'}))
    branch = forms.ModelChoiceField(queryset=Branch.objects.none(), widget=forms.Select(attrs={'class': 'block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ring-1 ring-slate-200 sm:text-sm h-10 px-3 transition-all'}))
    can_perform_credit_sales = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'h-5 w-5 rounded border-slate-300 text-blue-600 focus:ring-blue-500'}))

    class Meta:
        model = User
        fields = ['email']

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['branch'].queryset = Branch.objects.filter(tenant=tenant)

class OTPVerificationForm(forms.Form):
    otp_code = forms.CharField(max_length=6, min_length=6, widget=forms.TextInput(attrs={'class': 'block w-full text-center text-2xl tracking-widest rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ring-1 ring-slate-200 h-14 transition-all', 'placeholder': '000000'}))
    secret = forms.CharField(widget=forms.HiddenInput(), required=False)
