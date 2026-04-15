from django import forms
from django.contrib.auth.forms import UserCreationForm

from userauths.models import User

USER_TYPE = (
    ("Customer", "Customer"),
    ("Shop Owner", "Shop Owner"),
)

class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'h-10 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm outline-none focus:border-teal-500', 'placeholder':'Full Name'}), required=True)
    mobile = forms.CharField(widget=forms.TextInput(attrs={'class': 'h-10 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm outline-none focus:border-teal-500', 'placeholder':'Mobile Number'}), required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'h-10 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm outline-none focus:border-teal-500', 'placeholder':'Email Address'}), required=True)
    user_type = forms.ChoiceField(choices=USER_TYPE, widget=forms.Select(attrs={'class': 'h-10 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm outline-none focus:border-teal-500'}), required=True)
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'h-10 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm outline-none focus:border-teal-500', 'placeholder':'Password'}),
        required=True,
        help_text="Minimum 6 characters",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'h-10 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm outline-none focus:border-teal-500', 'placeholder':'Confirm Password'}),
        required=True,
    )

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']
       
class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'h-10 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm outline-none focus:border-teal-500', 'name': "email", 'placeholder':'Email Address'}), required=False)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'h-10 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm outline-none focus:border-teal-500', 'name': "password", 'placeholder':'Password'}), required=False)

    class Meta:
        model = User
        fields = ['email', 'password']
