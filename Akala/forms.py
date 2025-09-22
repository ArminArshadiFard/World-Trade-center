from django import forms
from .models import Product, Basket, Category, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class login_user(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class Add_to_basket(forms.ModelForm):
    class Meta:
        model = Basket
        fields = ['basket_product', 'basket_user']
        widgets = {
            'basket_product': forms.HiddenInput(),
            'basket_user': forms.HiddenInput(),
        }


class Createuserform(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class Add_product(forms.ModelForm):
    class Meta:
        model = Product
        prepopulated_fields = {'slug': ('name',), 'created_by': ('User',)}

        fields = ['category',
                  'created_by',
                  'name',
                  'description',
                  'image',
                  'price',
                  'discounted_price',
                  'in_stock',
                  'is_active',
                  'is_discount',
                  'slug',
                  'quantity']
        widgets = {
            'category': forms.Select(choices=Category.objects.all()),
            'created_by': forms.HiddenInput(),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discounted_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'in_stock': forms.CheckboxInput(),
            'is_active': forms.CheckboxInput(),
            'is_discount': forms.CheckboxInput(),
            'slug': forms.HiddenInput(),
            'quantity': forms.NumberInput(attrs={'min': '0'}, )
        }


class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = {'name', 'email', 'content'}
        widgets = {
            'name': forms.TextInput(attrs={'class': 'col-sm-12'}),
            'email': forms.TextInput(attrs={'class': 'col-sm-12'}),
            'content': forms.Textarea(attrs={'class': 'col-sm-12'}),
        }
