from django.urls import path
from .views import (PurchasePropertiesAPIView, AgentsTransactionLogsListView,
                    ClientTransactionLogsListView)

urlpatterns = [
    path('agent/', AgentsTransactionLogsListView.as_view(), name='agent_transactions_list'),
    path('client/', ClientTransactionLogsListView.as_view(), name='client_transactions_list'),
    path('buy_cart_items/', PurchasePropertiesAPIView.as_view(), name='purchase_properties'),
]
