from django import forms
from .models import Product, Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'nit', 'address', 'city', 'customer_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-slate-200 rounded-xl'}),
            'nit': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-slate-200 rounded-xl'}),
            'address': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-slate-200 rounded-xl'}),
            'city': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-slate-200 rounded-xl'}),
            'customer_type': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-slate-200 rounded-xl'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['code', 'name', 'description', 'composition', 'line', 'price', 'status']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-slate-200 rounded-xl'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-slate-200 rounded-xl'}),
            'description': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-slate-200 rounded-xl'}),
            'composition': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-slate-200 rounded-xl'}),
            'line': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-slate-200 rounded-xl'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-slate-200 rounded-xl'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-slate-200 rounded-xl'}),
        }
