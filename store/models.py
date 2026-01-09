from django.contrib import admin
from .models import Product, ProductImage, Order
from django.utils.html import format_html
import json


# =========================
# PRODUCT ADMIN
# =========================

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "price_usd", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    inlines = [ProductImageInline]


# =========================
# ORDER ADMIN
# =========================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "amount_total",
        "paid",
        "status",
        "payment_method",
    )

    list_filter = (
        "paid",
        "status",
        "payment_method",
        "created_at",
    )

    search_fields = (
        "id",
        "status",
        "payment_method",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "formatted_items",
    )

    fieldsets = (
        ("Order Info", {
            "fields": ("created_at", "status", "paid", "payment_method", "amount_total")
        }),
        ("Order Items", {
            "fields": ("formatted_items",),
        }),
    )

    def formatted_items(self, obj):
        """Pretty print JSON items"""
        return format_html(
            "<pre style='white-space:pre-wrap'>{}</pre>",
            json.dumps(obj.items, indent=2)
        )

    formatted_items.short_description = "Order Items"
