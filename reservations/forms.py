from datetime import timedelta
from django import forms
from django.core.exceptions    import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models                    import Reservation

class RegisterForm(UserCreationForm):
    email      = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name  = forms.CharField(max_length=30, required=False)

    class Meta:
        model  = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
        ]

class ReservationForm(forms.ModelForm):
    class Meta:
        model  = Reservation
        fields = ['start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type':'datetime-local'}),
            'end_time':   forms.DateTimeInput(attrs={'type':'datetime-local'}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_time')
        end   = cleaned.get('end_time')
        if start and end:
            if end <= start:
                raise ValidationError('End time must be after start time.')
            if end - start > timedelta(hours=1):
                raise ValidationError('You can only book up to 1 hour.')
        return cleaned
