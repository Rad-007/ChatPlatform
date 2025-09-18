from django.db import models
from django.contrib.auth.models import User


class PaymentOrder(models.Model):
    STATUS_CHOICES = (
        ("created", "Created"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_orders")
    amount = models.IntegerField(help_text="Amount in paise")
    currency = models.CharField(max_length=8, default="INR")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="created")

    # Razorpay fields
    razorpay_order_id = models.CharField(max_length=128, blank=True, db_index=True)
    razorpay_payment_id = models.CharField(max_length=128, blank=True)
    razorpay_signature = models.CharField(max_length=256, blank=True)

    receipt = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):  # pragma: no cover
        return f"Order {self.id} - {self.user.username} - {self.status}"

