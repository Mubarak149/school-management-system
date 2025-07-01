from django import forms
from django.contrib.auth.forms import AuthenticationForm
from custom_user.models import User
from django.contrib.auth import authenticate

        
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'id':"email",
            'class': 'form-control',
            'value': 'mk@gmail.com',
            'required': True
    }))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'id':"password",
            'class': 'form-control',
            'value': '12345678',
            'required': True
    }))
    
    class Meta:
        model = User
        fields = "__all__"

    def clean(self):
        # Get the cleaned data
        cleaned_data = super().clean()

        # Convert username or email to lowercase
        username = self.cleaned_data.get('username')
        if username:
            self.cleaned_data['username'] = username.lower()

        # Authenticate user
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
