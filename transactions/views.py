from rest_framework import (views, permissions)
from rest_framework.response import Response
from django.db import transaction


from .serializers import (
    AgentTransactionLogsListSerializer, 
    TransactionLogSerializer)
from authentication.permissions import IsAgent, IsCustomer
from .models import TransactionLog
from properties.models import ShoppingCart
from utils.paystack import chargeCard, generateTransactionReference
from notifications.models import Notifications

class AgentsTransactionLogsListView(views.APIView):

    serializer_class = AgentTransactionLogsListSerializer
    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def get(self,request):

        tx_logs = TransactionLog.objects.filter(agent=request.user).order_by("-created_at")

        serializer = self.serializer_class(tx_logs, many=True)

        return Response(serializer.data, status=200)



class ClientTransactionLogsListView(views.APIView):

    serializer_class = AgentTransactionLogsListSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def get(self, request):

        tx_logs = TransactionLog.objects.filter(client=request.user).order_by("-created_at")

        serializer = self.serializer_class(tx_logs, many=True)

        return Response(serializer.data, status=200)



class PurchasePropertiesAPIView(views.APIView):

    serializer_class = TransactionLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def post(self, request):

        with transaction.atomic():
            bulkLogs, notificationsList = [], []
            cart = ShoppingCart.objects.filter(user=request.user)

            for item in cart:

                property = item.property

                ## generate referenceId
                referenceId = generateTransactionReference()

                ## delete item from cart
                item.delete()

                # Queue Transaction
                payment_service_response = chargeCard()

                ## create Transaction Logs
                bulkLogs.append(
                    TransactionLog(**{
                        "property_name": property.name,
                        "reference": referenceId,
                        "property": property,
                        "client": request.user,
                        "agent": property.agent,
                        "number_of_shares": item.quantity,
                        "amount": property.price_per_share,
                        **payment_service_response
                    }))

                ## save notifications object
                payment_status = payment_service_response.get('status')
                notification_message = f'{payment_status} transaction for property {property.id}'
                notificationsList.extend([
                    {"user": request.user, "message": notification_message}, ##notify client
                    {"user": property.agent, "message": notification_message} ##notify agent
                    ])

            transactionLogs = TransactionLog.objects.bulk_create(bulkLogs)

            ## send notifications
            Notifications.new_bulk_entry(notificationsList)

            serializer = self.serializer_class(transactionLogs, many=True)

        return Response(serializer.data, status=200)



