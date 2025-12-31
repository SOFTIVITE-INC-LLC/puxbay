from django import forms
from .models import StockTransfer, StockTransferItem
from accounts.models import Branch
from main.models import Product

class StockTransferForm(forms.ModelForm):
    class Meta:
        model = StockTransfer
        fields = ['destination_branch', 'notes']
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.branch_id = kwargs.pop('branch_id', None)
        super(StockTransferForm, self).__init__(*args, **kwargs)
        
        if self.user:
            tenant = self.user.profile.tenant
            current_branch_id = self.branch_id
            
            # Destination cannot be the same as source
            self.fields['destination_branch'].queryset = Branch.objects.filter(
                tenant=tenant
            ).exclude(id=current_branch_id)
