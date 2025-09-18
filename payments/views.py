import uuid
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseBadRequest
from django.middleware.csrf import get_token
from .models import PaymentOrder
import razorpay


def _razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def upgrade(request):
    # Create an order upfront for simplicity
    amount = settings.PRO_MONTHLY_PRICE
    currency = settings.PAYMENT_CURRENCY
    receipt = f"rcpt_{uuid.uuid4().hex[:10]}"
    order = PaymentOrder.objects.create(user=request.user, amount=amount, currency=currency, receipt=receipt)

    client = _razorpay_client()
    rzp_order = client.order.create({
        "amount": amount,
        "currency": currency,
        "receipt": receipt,
        "payment_capture": 1,
    })
    order.razorpay_order_id = rzp_order.get("id", "")
    order.save()

    ctx = {
        "key_id": settings.RAZORPAY_KEY_ID,
        "order": rzp_order,
        "amount_display": f"₹{amount/100:.2f}",
        "currency": currency,
        "csrf_token": get_token(request),
        "user_email": request.user.email or "test@example.com",
        "user_name": request.user.get_full_name() or request.user.username,
    }
    return render(request, "payments/upgrade.html", ctx)


@login_required
@require_http_methods(["POST"])
def verify(request):
    order_id = request.POST.get("razorpay_order_id")
    payment_id = request.POST.get("razorpay_payment_id")
    signature = request.POST.get("razorpay_signature")
    if not (order_id and payment_id and signature):
        return HttpResponseBadRequest("Missing parameters")

    try:
        order = PaymentOrder.objects.get(razorpay_order_id=order_id, user=request.user)
    except PaymentOrder.DoesNotExist:
        return HttpResponseBadRequest("Order not found")

    client = _razorpay_client()
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })
    except razorpay.errors.SignatureVerificationError:
        order.status = "failed"
        order.razorpay_payment_id = payment_id
        order.razorpay_signature = signature
        order.save()
        return render(request, "payments/failure.html", {"order": order})

    # Mark paid and upgrade plan
    order.status = "paid"
    order.razorpay_payment_id = payment_id
    order.razorpay_signature = signature
    order.save()

    profile = getattr(request.user, "profile", None)
    if profile:
        profile.plan = "pro"
        profile.save()

    return render(request, "payments/success.html", {"order": order})

