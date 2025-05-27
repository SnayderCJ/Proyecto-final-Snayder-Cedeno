# forms.py
from django import forms
import pytz

class SettingsForm(forms.Form):
    language = forms.ChoiceField(
        choices=[('Español', 'Español')],
        label='Idioma (Más Próximamente)...',
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'readonly': 'readonly'
        })
    )
    timezone = forms.ChoiceField(
        choices=[(tz, tz) for tz in pytz.common_timezones],
        label='Zona Horaria',
        widget=forms.Select(attrs={'class': 'input-field'})
    )
