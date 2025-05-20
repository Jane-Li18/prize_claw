from django import forms
from .models import Prize

class PrizeForm(forms.ModelForm):
    class Meta:
        model = Prize
        fields = ['name', 'description', 'image', 'probability']
