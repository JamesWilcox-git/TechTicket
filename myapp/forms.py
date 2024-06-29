from django import forms
from .models import CustomUser, Ticket

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user.is_authenticated and user.user_type == 'admin':
            self.fields['user_type'].choices = CustomUser.USER_TYPE_CHOICES
        else:
            self.fields['user_type'].choices = [
                choice for choice in CustomUser.USER_TYPE_CHOICES if choice[0] == 'normal'
            ]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if self.cleaned_data["user_type"] == "admin":
            user.is_superuser = True
            user.is_staff = True
        if self.cleaned_data["user_type"] == "employee":
            user.is_staff = True
        if commit:
            user.save()
        return user

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['category', 'description']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
