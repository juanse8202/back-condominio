# pagos/urls.py
from django.urls import path
from .views import (
    CreatePaymentIntentView,
    ConfirmPaymentView,
    payment_history,
)

urlpatterns = [
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    path('confirm-payment/', ConfirmPaymentView.as_view(), name='confirm_payment'),
    path('historial/', payment_history, name='payment_history'),
]

