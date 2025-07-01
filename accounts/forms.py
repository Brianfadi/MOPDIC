from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AdminPasswordChangeForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """A form for creating new users with email as the username field."""
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        help_text=_("Your password must contain at least 8 characters and can't be too common or entirely numeric."),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("A user with that email already exists."))
        return email.lower()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """A form for updating users with proper password hashing."""
    password = None  # Remove the password field from the form

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser',
                 'groups', 'user_permissions', 'last_login', 'date_joined')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_login': forms.DateTimeInput(attrs={'class': 'form-control', 'disabled': True}),
            'date_joined': forms.DateTimeInput(attrs={'class': 'form-control', 'disabled': True}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_("A user with that email already exists."))
        return email.lower()


class ProfileUpdateForm(forms.ModelForm):
    """A form for users to update their profile information."""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'profile_picture', 'phone_number', 
                 'date_of_birth', 'address', 'city', 'country', 'postal_code', 'bio')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class CustomPasswordChangeForm(AdminPasswordChangeForm):
    """A form for changing a user's password in the admin interface."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
