from django.db import transaction
from decimal import Decimal
from django.utils import timezone
from .models import Wallet
from transactions.models import Transaction


@transaction.atomic
def credit_wallet(*, user, amount, reference, provider, raw_response=None):
    wallet = Wallet.objects.select_for_update().get(user=user)

    txn, created = Transaction.objects.get_or_create(
        reference=reference,
        defaults={
            "user": user,
            "amount": amount,
            "transaction_type": Transaction.Type.CREDIT,
            "provider": provider,
            "status": Transaction.Status.PENDING,
            "raw_response": raw_response,
        },
    )

    if not created and txn.status == Transaction.Status.SUCCESS:
        return wallet.balance  # idempotent

    wallet.balance += Decimal(amount)
    wallet.save(update_fields=["balance"])

    txn.status = Transaction.Status.SUCCESS
    txn.verified_at = timezone.now()
    txn.save(update_fields=["status", "verified_at"])

    return wallet.balance


@transaction.atomic
def debit_wallet(*, user, amount, reference, provider):
    wallet = Wallet.objects.select_for_update().get(user=user)

    if wallet.balance < Decimal(amount):
        raise ValueError("Insufficient balance")

    txn = Transaction.objects.create(
        user=user,
        amount=amount,
        transaction_type=Transaction.Type.DEBIT,
        provider=provider,
        reference=reference,
        status=Transaction.Status.PENDING,
    )

    wallet.balance -= Decimal(amount)
    wallet.save(update_fields=["balance"])

    txn.status = Transaction.Status.SUCCESS
    txn.verified_at = timezone.now()
    txn.save(update_fields=["status", "verified_at"])

    return wallet.balance
