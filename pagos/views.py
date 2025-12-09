# pagos/views.py

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings

import stripe
import os
from dotenv import load_dotenv

from .models import Pago
from .serializers import (
    PagoSerializer,
    CreatePaymentIntentSerializer,
    ConfirmPaymentSerializer
)
from gestion.models import Propietario
from areas_comunes.models import ReservaAreaComun
from administracion.models import PerfilUsuario

# ============================
# CONFIGURACIÓN STRIPE
# ============================
load_dotenv()
stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", None) or os.getenv("STRIPE_SECRET_KEY")


# ============================
# CREAR PAYMENT INTENT
# ============================
class CreatePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            print("🔵 CREATE PAYMENT INTENT")

            # ✅ VALIDAR PERFIL Y ROL
            try:
                perfil = PerfilUsuario.objects.get(user=request.user)
                rol_nombre = perfil.rol.nombre if perfil.rol else None
            except PerfilUsuario.DoesNotExist:
                return Response({"success": False, "message": "Perfil no encontrado"}, status=403)

            if rol_nombre not in ["PROPIETARIO", "INQUILINO"]:
                return Response({"success": False, "message": "No autorizado"}, status=403)

            # ✅ VALIDAR DATOS
            serializer = CreatePaymentIntentSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({"success": False, "errors": serializer.errors}, status=400)

            propietario = Propietario.objects.get(user=request.user)
            reserva_id = serializer.validated_data["reserva_id"]
            reserva = get_object_or_404(ReservaAreaComun, id=reserva_id)

            if reserva.propietario != propietario:
                return Response({"success": False, "message": "Reserva no pertenece al usuario"}, status=403)

            if reserva.estado != "pendiente":
                return Response({"success": False, "message": f"Reserva ya está {reserva.estado}"}, status=400)

            if Pago.objects.filter(reserva=reserva, estado="completado").exists():
                return Response({"success": False, "message": "Esta reserva ya fue pagada"}, status=400)

            amount = float(serializer.validated_data["amount"])
            amount_cents = int(amount * 100)

            # ✅ STRIPE SOLO ACEPTA USD, EUR, MXN, etc.
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency="usd",
                payment_method_types=["card"],
                metadata={
                    "reserva_id": reserva.id,
                    "propietario_id": propietario.id
                }
            )

            area_nombre = reserva.area_comun.nombre if reserva.area_comun else "Área"

            pago = Pago.objects.create(
                propietario=propietario,
                reserva=reserva,
                tipo_pago="reserva",
                monto=amount,
                moneda="USD",
                payment_intent_id=payment_intent.id,
                estado="pendiente",
                descripcion=f"Pago de reserva - {area_nombre}"
            )

            print("✅ PAYMENT INTENT CREADO:", payment_intent.id)

            return Response({
                "success": True,
                "payment_intent_id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "pago_id": pago.id,
                "amount": amount
            }, status=200)

        except Exception as e:
            print("❌ ERROR CREATE PAYMENT:", str(e))
            return Response({
                "success": False,
                "message": "Error interno al crear el pago",
                "error": str(e)
            }, status=500)


# ============================
# CONFIRMAR PAGO
# ============================
class ConfirmPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = ConfirmPaymentSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({"success": False, "errors": serializer.errors}, status=400)

            payment_intent_id = serializer.validated_data["payment_intent_id"]

            pago = get_object_or_404(Pago, payment_intent_id=payment_intent_id)

            if pago.propietario.user != request.user:
                return Response({"success": False, "message": "No autorizado"}, status=403)

            payment_method = stripe.PaymentMethod.create(
                type="card",
                card={
                    "number": serializer.validated_data["card_number"],
                    "exp_month": int(serializer.validated_data["exp_month"]),
                    "exp_year": int("20" + serializer.validated_data["exp_year"]),
                    "cvc": serializer.validated_data["cvc"],
                }
            )

            intent = stripe.PaymentIntent.confirm(
                payment_intent_id,
                payment_method=payment_method.id
            )

            pago.payment_method_id = payment_method.id

            if intent.status == "succeeded":
                pago.estado = "completado"
                pago.fecha_completado = timezone.now()
                pago.charge_id = intent.charges.data[0].id if intent.charges.data else None

                if pago.reserva:
                    pago.reserva.estado = "confirmada"
                    pago.reserva.save()
            else:
                pago.estado = "fallido"

            pago.save()

            return Response({
                "success": True,
                "estado": pago.estado,
                "payment_intent_status": intent.status,
                "pago_id": pago.id
            })

        except stripe.error.CardError as e:
            return Response({"success": False, "message": e.user_message}, status=400)

        except Exception as e:
            print("❌ ERROR CONFIRM PAYMENT:", str(e))
            return Response({"success": False, "message": "Error interno", "error": str(e)}, status=500)


# ============================
# HISTORIAL DE PAGOS
# ============================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def payment_history(request):
    try:
        propietario_id = request.query_params.get("propietario")

        if not propietario_id:
            return Response({"success": False, "message": "ID requerido"}, status=400)

        propietario = get_object_or_404(Propietario, id=propietario_id)

        if propietario.user != request.user:
            return Response({"success": False, "message": "No autorizado"}, status=403)

        pagos = Pago.objects.filter(propietario=propietario).order_by("-fecha_creacion")
        serializer = PagoSerializer(pagos, many=True)

        return Response({"success": True, "data": serializer.data})

    except Exception as e:
        print("❌ ERROR HISTORIAL:", str(e))
        return Response({"success": False, "message": "Error interno"}, status=500)
