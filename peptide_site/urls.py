from django.contrib import admin
from django.urls import path
from store import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("admin/", admin.site.urls),
    path("about/", views.about, name="about"),
    path("", views.home, name="home"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("products/", views.product_list, name="product_list"),
    path("checkout/", views.checkout, name="checkout"),
    # Demo API endpoint for cart/checkout wiring (replace with real DRF later)
    path("api/health/", views.api_health, name="api_health"),
    path("api/payments/crypto/create/", views.create_crypto_invoice, name="crypto_create"),
    path("api/payments/crypto/webhook/", views.nowpayments_webhook, name="crypto_webhook"),
    path("checkout/success/", views.checkout_success, name="checkout_success"),
    path("checkout/cancel/", views.checkout_cancel, name="checkout_cancel"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
