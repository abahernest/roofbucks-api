from rest_framework import serializers

from .models import TransactionLog
from properties.serializers import ShoppingCartSerializer


class TransactionLogSerializer (serializers.ModelSerializer):

    class Meta:
        model = TransactionLog
        fields = '__all__'

class AgentTransactionLogsListSerializer (serializers.ModelSerializer):

    class Meta:
        model = TransactionLog
        fields = ["reference", "property_name", "property",
         "status", "amount", "number_of_shares", "created_at"]


class ClientTransactionLogsListSerializer (serializers.ModelSerializer):

    class Meta:
        model = TransactionLog
        fields = ["reference", "property_name", "property",
                  "status", "amount", "number_of_shares", "created_at"]



