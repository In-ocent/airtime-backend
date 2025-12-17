from django.db import models
from decimal import Decimal
from django.conf import settings

# Create your models here.

User = settings.AUTH_USER_MODEL


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("00.00"))
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - ₦{self.balance}"
