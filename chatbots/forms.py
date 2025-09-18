from django import forms
from .models import Bot

class BotForm(forms.ModelForm):
    class Meta:
        model = Bot
        fields = [
            "name",
            "description",
            "welcome_message",
            "primary_color",
            "position",
            "system_prompt",
            "model_name",
            "temperature",
            "is_active",
        ]
