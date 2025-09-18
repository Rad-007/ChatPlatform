from django.db import models
from django.contrib.auth.models import User
import secrets


class Bot(models.Model):
    """A chatbot owned by a user with customizable design and AI settings."""

    POSITION_CHOICES = (
        ("bottom-right", "Bottom Right"),
        ("bottom-left", "Bottom Left"),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bots")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    welcome_message = models.CharField(max_length=255, default="Hi! How can I help you today?")

    # Appearance
    primary_color = models.CharField(max_length=7, default="#4F46E5")  # HEX
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default="bottom-right")

    # AI settings
    system_prompt = models.TextField(
        default="You are a helpful assistant for this website. Answer concisely and helpfully."
    )
    model_name = models.CharField(max_length=100, default="llama3-8b-8192")
    temperature = models.FloatField(default=0.4)

    # Access
    token = models.CharField(max_length=64, unique=True, editable=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.token:
            # 32 bytes hex token
            self.token = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} ({self.owner.username})"

