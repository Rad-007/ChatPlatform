from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Conversation(models.Model):
    """A conversation between a site visitor and a bot."""

    from chatbots.models import Bot  # type: ignore  # local import to avoid circular

    bot = models.ForeignKey('chatbots.Bot', on_delete=models.CASCADE, related_name='conversations')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    session_id = models.CharField(max_length=64, db_index=True)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):  # pragma: no cover
        return f"Conv {self.id} - {self.bot.name}"


class Message(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System"),
    )

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):  # pragma: no cover
        return f"{self.role}: {self.content[:30]}"

