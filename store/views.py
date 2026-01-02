from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone

from .models import Product


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
def product_list(request):
    products = Product.objects.filter(is_active=True).order_by("-id")
    return render(request, "products.html", {
        "products": products
    })