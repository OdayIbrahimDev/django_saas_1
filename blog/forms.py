from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    customer_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name'
        })
    )
    customer_phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
    )
    customer_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Street Address, City, State, Zip Code'
        })
    )

    class Meta:
        model = Order
        fields = ['customer_name', 'customer_phone', 'customer_address']
