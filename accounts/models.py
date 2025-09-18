from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    ROLE_CHOICES = (
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("viewer", "Viewer"),
    )
    PLAN_CHOICES = (
        ("free", "Free"),
        ("pro", "Pro"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default="owner")
    plan = models.CharField(max_length=16, choices=PLAN_CHOICES, default="free")
    organization = models.CharField(max_length=120, blank=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user.username} ({self.role}, {self.plan})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()

