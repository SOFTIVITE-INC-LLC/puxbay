from django import forms
from .models import StorefrontSettings, ProductReview, NewsletterSubscription, Customer
from main.models import Order

class StorefrontSettingsForm(forms.ModelForm):
    class Meta:
        model = StorefrontSettings
        exclude = ['tenant', 'created_at', 'updated_at']
        widgets = {
            'store_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-blue-500 focus:border-blue-500'}),
            'slug': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-blue-500 focus:border-blue-500'}),
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'h-10 w-20 p-1 border rounded cursor-pointer'}),
            'welcome_message': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 border rounded-lg'}),
            'about_text': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-2 border rounded-lg'}),
            'delivery_fee': forms.NumberInput(attrs={'step': '0.01', 'class': 'w-full px-4 py-2 border rounded-lg'}),
            'min_order_amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'w-full px-4 py-2 border rounded-lg'}),
            
            # Boolean Fields (Hidden for toggle UI)
            'is_active': forms.CheckboxInput(attrs={'class': 'sr-only peer'}),
            'allow_pickup': forms.CheckboxInput(attrs={'class': 'sr-only peer'}),
            'allow_delivery': forms.CheckboxInput(attrs={'class': 'sr-only peer'}),
            'enable_stripe': forms.CheckboxInput(attrs={'class': 'sr-only peer'}),
            'enable_paystack': forms.CheckboxInput(attrs={'class': 'sr-only peer'}),

            # File Inputs
            'logo_image': forms.FileInput(attrs={'class': 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 border border-slate-200 rounded-lg cursor-pointer'}),
            'banner_image': forms.FileInput(attrs={'class': 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 border border-slate-200 rounded-lg cursor-pointer'}),

            # Payment Keys (Password widgets for security visual)
            'stripe_public_key': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg font-mono text-sm'}),
            'stripe_secret_key': forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg font-mono text-sm', 'render_value': True}),
            'paystack_public_key': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg font-mono text-sm'}),
            'paystack_secret_key': forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg font-mono text-sm', 'render_value': True}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter branches to tenant's branches only
        if self.instance and self.instance.tenant:
            self.fields['default_branch'].queryset = self.instance.tenant.branches.all()
            self.fields['default_branch'].widget.attrs.update({'class': 'w-full px-4 py-2 border rounded-lg'})

class CustomerRegistrationForm(forms.Form):
    name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Full Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Email Address'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Phone Number'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Confirm Password'}))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class CustomerLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Email Address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Password'}))

class CheckoutForm(forms.Form):
    PAYMENT_METHODS = (
        ('cash', 'Cash on Delivery'),
        ('stripe', 'Credit/Debit Card (Stripe)'),
        ('paystack', 'Mobile Money/Card (Paystack)'),
        ('loyalty_points', 'Loyalty Points'),
    )
    name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl bg-white/50 focus:ring-2 focus:ring-blue-500 transition-all', 'placeholder': 'Full Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl bg-white/50 focus:ring-2 focus:ring-blue-500 transition-all', 'placeholder': 'Email Address'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl bg-white/50 focus:ring-2 focus:ring-blue-500 transition-all', 'placeholder': 'Phone Number'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-3 border rounded-xl bg-white/50 focus:ring-2 focus:ring-blue-500 transition-all', 'placeholder': 'Delivery Address'}), required=False)
    payment_method = forms.ChoiceField(choices=PAYMENT_METHODS, widget=forms.RadioSelect(attrs={'class': 'sr-only peer'}))

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 transition-all', 'placeholder': 'Share your thoughts about this product...'}),
        }

class NewsletterSubscriptionForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'w-full px-6 py-4 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/30 transition-all', 'placeholder': 'Enter your email address'}),
        }

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500'}),
        }

class CouponApplyForm(forms.Form):
    code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Coupon Code', 'class': 'w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500'}))

class TrackOrderForm(forms.Form):
    order_id = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Order ID / Email', 'class': 'w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 transition-all'}))

class ContactForm(forms.Form):
    name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 transition-all', 'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 transition-all', 'placeholder': 'Your Email'}))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 transition-all', 'placeholder': 'Subject'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'class': 'w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 transition-all', 'placeholder': 'Your Message'}))
