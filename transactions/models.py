from django.db import models
from django.conf import settings
import uuid

User = settings.AUTH_USER_MODEL


class Transaction(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    class Type(models.TextChoices):
        CREDIT = "credit", "Credit"
        DEBIT = "debit", "Debit"

    class Provider(models.TextChoices):
        PAYSTACK = "paystack", "Paystack"
        INTERNAL = "internal", "Internal"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transactions")

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    transaction_type = models.CharField(max_length=10, choices=Type.choices)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )

    provider = models.CharField(
        max_length=20, choices=Provider.choices, default=Provider.INTERNAL
    )

    reference = models.CharField(max_length=100, unique=True, db_index=True)

    raw_response = models.JSONField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} | {self.transaction_type} | ₦{self.amount} | {self.status}"
