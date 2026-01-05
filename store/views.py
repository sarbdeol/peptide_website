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
        "success_url": "https://retacuretide.com//checkout/success",
        "cancel_url": "https://retacuretide.com/checkout/cancel",
        "ipn_callback_url": "https://retacuretide.com/api/payments/crypto/webhook/",
    }
    print(NOWPAYMENTS_API_KEY)
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


@api_view(["POST"])
@permission_classes([])
def nowpayments_webhook(request):

    if not verify_nowpayments_signature(request):
        return Response({"error": "Invalid signature"}, status=403)

    data = request.data
    temp_id = data.get("order_id")
    status_code = data.get("payment_status")

    if status_code not in ("confirmed", "finished"):
        return Response({"message": "Ignored"}, status=200)


    temp = get_object_or_404(TempCart, id=temp_id)
    info = temp.data

    order = Order.objects.create(
        name=info["customer"].get("name", ""),
        email=info["customer"].get("email", ""),
        phone=info["customer"].get("phone", ""),
        address=json.dumps(info["address"]),
        items=info["items"],
        subtotal=info["subtotal"],
        shipping_cost=info["shipping_cost"],
        amount_total=info["amount_total"],
        paid=True,
        status="Paid",
    )

    order.add_timeline_event("paid", "Crypto payment via NOWPayments")
    temp.delete()

    return Response({"success": True})



def checkout_success(request):
    return render(request, "success.html")

def checkout_cancel(request):
    return render(request, "cancel.html")