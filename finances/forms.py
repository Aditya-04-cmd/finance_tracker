from django import forms
from .models import Transaction, Category
from django.utils import timezone

class DateInput(forms.DateInput):
    input_type = 'date'

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type']

class TransactionForm(forms.ModelForm):
    date = forms.DateField(widget=DateInput(), initial=timezone.now)

    class Meta:
        model = Transaction
        fields = ['amount', 'description', 'date', 'category', 'transaction_type']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TransactionForm, self).__init__(*args, **kwargs)

        if self.user:
            self.fields['category'].queryset = Category.objects.filter(user=self.user)

class DateRangeFilterForm(forms.Form):
    start_date = forms.DateField(widget=DateInput(), required=False)
    end_date = forms.DateField(widget=DateInput(), required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.none(), required=False)
    transaction_type = forms.ChoiceField(choices=[('', 'All'), ('expense', 'Expense'), ('income', 'Income')], required=False)
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(DateRangeFilterForm, self).__init__(*args, **kwargs)
        
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
