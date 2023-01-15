from django.db import models

from properties.models import Property
from users.models import User

CHOICES_FOR_STATUS = [
    ("PENDING", "Pending Payment"),
    ("SUCCESS", "Successful Payment"),
    ("FAILED", "Failed Payment")
]

CHOICES_FOR_PAYMENT_METHOD = [
    ("PAYSTACK", "Paystack Payment Service")
]

class TransactionLog(models.Model):

    property_name   = models.CharField(max_length=256, blank=True, null=True)
    reference       = models.CharField(max_length=256)
    property        = models.ForeignKey(Property, on_delete=models.CASCADE)
    agent           = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transaction_logs_agent")
    client          = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transaction_logs_client")
    amount          = models.PositiveBigIntegerField()
    number_of_shares = models.IntegerField()
    status = models.CharField(
        max_length=256,
        choices=CHOICES_FOR_STATUS,
        default=CHOICES_FOR_STATUS[0][0])
    payment_method      = models.CharField(
        max_length=256, 
        choices= CHOICES_FOR_PAYMENT_METHOD,
        default = CHOICES_FOR_PAYMENT_METHOD[0][0])
    error_message_from_payment_service = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "TransactionLogs"

        

