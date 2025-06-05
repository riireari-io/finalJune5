from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control rounded-3'}),
        max_length=30,
        required=True
    )
    
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control rounded-3'}),
        max_length=30,
        required=True
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control rounded-3'}),
        required=True
    )
    
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Phone Number (e.g. 639xxxxxxxxx)', 
            'class': 'form-control rounded-3',
            'pattern': '^63[0-9]{10}$',
            'title': 'Phone number must start with 63 followed by 10 digits'
        }),
        required=True,
        
    )

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone:
            raise forms.ValidationError('Phone number is required')
        if not phone.startswith('63'):
            raise forms.ValidationError('Phone number must start with 63')
        if not phone[2:].isdigit():
            raise forms.ValidationError('Phone number must contain only digits after 63')
        if len(phone) != 12:
            raise forms.ValidationError('Phone number must be exactly 12 digits (63 + 10 digits)')
        return phone
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control rounded-3'}),
        required=True
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control rounded-3'}),
        required=True
    )
    
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')


class CustomUserLoginForm(forms.Form):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control rounded-3'}),
        required=True
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control rounded-3'}),
        required=True
    )


class EmailPhishingQuizForm(forms.Form):
    q1 = forms.ChoiceField(
        label="Which of the following is a common sign of a phishing email?",
        choices=[
            ("a", "A personalized greeting from your bank"),
            ("b", "A request for your password or sensitive info"),
            ("c", "An email from a known contact with no links")
        ],
        widget=forms.RadioSelect,
        required=True
    )


class AdminUserCreationForm(CustomUserCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user

