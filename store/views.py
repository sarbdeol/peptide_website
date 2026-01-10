from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
import requests
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from django.conf import settings
from .models import Product
from .models import TempCart, Order
from django.views.decorators.csrf import csrf_exempt
NOWPAYMENTS_API_KEY = settings.NOWPAYMENTS_API_KEY
IPN_SECRET = settings.NOWPAYMENTS_IPN_SECRET
NOWPAYMENTS_INVOICE_URL = settings.NOWPAYMENTS_INVOICE_URL
def home(request):
    """
    Homepage – list active products
    """
    products = Product.objects.filter(is_active=True).order_by("-created_at")

    return render(
        request,
        "home.html",
        {
            "products": products,
            "now": timezone.now(),
        }
    )


def product_detail(request, slug):
    """
    Product detail page
    """
    product = get_object_or_404(
        Product,
        slug=slug,
        is_active=True
    )

    return render(
        request,
        "product_detail.html",
        {
            "product": product,
            "now": timezone.now(),
        }
    )


def checkout(request):
    """
    Checkout page (placeholder for now)
    """
    return render(
        request,
        "checkout.html",
        {
            "now": timezone.now(),
        }
    )


def api_health(request):
    """
    Simple health check
    """
    return JsonResponse(
        {
            "ok": True,
            "ts": timezone.now().isoformat(),
        }
    )

def about(request):
    return render(request, "about.html")
from django.db.models import Q

def product_list(request):
    query = request.GET.get("q", "").strip()

    products = Product.objects.filter(is_active=True)

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query)
        )

    products = products.order_by("-id")

    return render(request, "products.html", {
        "products": products,
        "query": query,
    })





@csrf_exempt
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def create_crypto_invoice(request):
    data = request.data
    print(data)
    items = data.get("items", [])
    customer = data.get("customer", {})
    address = data.get("address", {})
    area_id = data.get("area_id")

    if not items:
        return Response({"error": "items required"}, status=400)

    enriched_items = []
    subtotal = 0.0
    total_weight = 0.0

    for entry in items:
        product = get_object_or_404(Product, slug=entry["sku"])
        qty = int(entry["qty"])
        price = float(product.price_usd)

        subtotal += price * qty
        # total_weight += (product.weight_grams or 0) * qty

        enriched_items.append({
            "id": product.id,
            "title": product.name,
            "qty": qty,
            "price": price,
            "image": product.images.first().image.url if product.images.first() else "",
        })

    shipping_cost = 0.0  # peptides: usually fixed or free
    amount_total = subtotal + shipping_cost

    temp = TempCart.objects.create(data={
        "customer": customer,
        "address": address,
        "items": enriched_items,
        "subtotal": subtotal,
        "shipping_cost": shipping_cost,
        "amount_total": amount_total,
        "crypto": {}
    })

    payload = {
        "price_amount": round(amount_total, 2),
        "price_currency": "usd",
        "is_fixed_rate": True,
        "order_id": str(temp.id),
        "order_description": f"PeptideLab Order #{temp.id}",
        "success_url": "https://retacuretide.com/checkout/success",
        "cancel_url": "https://retacuretide.com/checkout/cancel",
        "ipn_callback_url": "https://retacuretide.com/api/payments/crypto/webhook/",
    }
    print(NOWPAYMENTS_INVOICE_URL)
    headers = {
        "x-api-key": NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json",
    }

    res = requests.post(NOWPAYMENTS_INVOICE_URL, json=payload, headers=headers)
    if res.status_code != 200:
        return Response({"error": res.text}, status=500)

    invoice = res.json()
    temp.data["crypto"] = {
        "invoice_id": invoice.get("id"),
        "invoice_url": invoice.get("invoice_url"),
    }
    temp.save()

    return Response({"invoice_url": invoice["invoice_url"]})



import hmac, hashlib, json
def verify_nowpayments_signature(request):
    received = request.headers.get("x-nowpayments-sig")
    if not received:
        return False

    body = request.body
    expected = hmac.new(
        IPN_SECRET.encode(),
        body,
        hashlib.sha512
    ).hexdigest()

    return hmac.compare_digest(received, expected)

@csrf_exempt
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def nowpayments_webhook(request):

    # 🔐 Verify NOWPayments signature
    if not verify_nowpayments_signature(request):
        return Response({"error": "Invalid signature"}, status=403)

    data = request.data

    temp_id = data.get("order_id")
    payment_status = data.get("payment_status")

    # Only accept completed payments
    if payment_status not in ("confirmed", "finished"):
        return Response({"message": "Payment not completed"}, status=200)

    # Fetch temp cart
    temp = get_object_or_404(TempCart, id=temp_id)
    info = temp.data  # this is your original checkout payload

    # 💰 Calculate totals safely
    subtotal = float(info.get("subtotal", 0))
    shipping = float(info.get("shipping_cost", 0))
    total = float(info.get("amount_total", subtotal + shipping))

    # ✅ Create Order (ONLY valid fields)
    order = Order.objects.create(
        items={
            "cart": info.get("items", []),
            "customer": info.get("customer", {}),
            "address": info.get("address", {}),
            "subtotal": subtotal,
            "shipping": shipping,
            "payment_provider": "nowpayments",
            "nowpayments_payload": data,  # full webhook payload (audit-safe)
        },
        amount_total=total,
        paid=True,
        status="Paid",
        payment_method="crypto",
    )

    # 🧹 Cleanup temp cart
    temp.delete()

    return Response({
        "success": True,
        "order_id": order.id
    })



def checkout_success(request):
    return render(request, "success.html")

def checkout_cancel(request):
    return render(request, "cancel.html")