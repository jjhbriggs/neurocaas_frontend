from django import forms
from .models import User, IAM
from django.contrib.auth.forms import ReadOnlyPasswordHashField


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    # password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    # password2 = forms.CharField(label='Password confirmation',
    #                             widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.CharField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    #first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={'class': 'form-control'}))
    #last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        #fields = ('email', 'first_name', 'last_name')
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        # user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for change users. Includes all the required
        fields, plus a repeated password."""

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password',)

    def clean_password(self):
        return self.initial["password"]


class UserLoginForm(forms.ModelForm):
    """A form for user login by aws credentials"""

    class Meta:
        model = IAM
        fields = ('aws_access_key', 'aws_secret_access_key',)

    aws_access_key = forms.CharField(label='AWS Access Key', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'id': 'aws_access_key',
            'type': 'text'
        }
    ))
    aws_secret_access_key = forms.CharField(label='AWS Secret Access Key', widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'id': 'aws_secret_access_key',
        }
    ))


class ProfileChangeForm(forms.ModelForm):
    """A form for change user's detail"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name',)
