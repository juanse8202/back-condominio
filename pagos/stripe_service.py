import stripe
from django.conf import settings
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """
    Servicio para manejar pagos con Stripe
    """
    
    @staticmethod
    def create_payment_intent(amount, currency='usd', metadata=None):
        """
        Crea un Payment Intent en Stripe
        
        Args:
            amount: Monto en centavos (ej: 10000 = $100.00)
            currency: Código de moneda (usd, bob, etc)
            metadata: Diccionario con información adicional
        
        Returns:
            dict: Información del Payment Intent
        """
        try:
            # Convertir BOB a USD para Stripe (tasa aproximada: 1 USD = 6.9 BOB)
            if currency == 'bob':
                amount_usd = float(amount) / 6.9
                amount_cents = int(amount_usd * 100)
                currency = 'usd'
            else:
                amount_cents = int(float(amount) * 100)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            
            return {
                'success': True,
                'payment_intent_id': payment_intent.id,
                'client_secret': payment_intent.client_secret,
                'amount': amount_cents,
                'currency': currency,
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    @staticmethod
    def confirm_payment(payment_intent_id, payment_method_data):
        """
        Confirma un pago con los datos de la tarjeta
        
        Args:
            payment_intent_id: ID del Payment Intent
            payment_method_data: Datos de la tarjeta
        
        Returns:
            dict: Resultado de la confirmación
        """
        try:
            # Crear método de pago
            payment_method = stripe.PaymentMethod.create(
                type='card',
                card={
                    'number': payment_method_data.get('card_number').replace(' ', ''),
                    'exp_month': payment_method_data.get('exp_month'),
                    'exp_year': payment_method_data.get('exp_year'),
                    'cvc': payment_method_data.get('cvc'),
                }
            )
            
            # Confirmar el Payment Intent
            payment_intent = stripe.PaymentIntent.confirm(
                payment_intent_id,
                payment_method=payment_method.id,
            )
            
            return {
                'success': True,
                'status': payment_intent.status,
                'payment_intent': payment_intent,
            }
        except stripe.error.CardError as e:
            return {
                'success': False,
                'error': e.user_message or str(e),
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    @staticmethod
    def retrieve_payment_intent(payment_intent_id):
        """
        Recupera información de un Payment Intent
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'success': True,
                'payment_intent': payment_intent,
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    @staticmethod
    def refund_payment(payment_intent_id, amount=None):
        """
        Reembolsa un pago
        
        Args:
            payment_intent_id: ID del Payment Intent
            amount: Monto a reembolsar en centavos (None = reembolso total)
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            charge_id = payment_intent.latest_charge
            
            refund_params = {'charge': charge_id}
            if amount:
                refund_params['amount'] = amount
            
            refund = stripe.Refund.create(**refund_params)
            
            return {
                'success': True,
                'refund': refund,
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e),
            }
