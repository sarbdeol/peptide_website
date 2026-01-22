from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

EXEMPT_PATHS = (
    "/admin/",
    "/password/",
    "/api/payments/",   # allow crypto + webhooks
    "/static/",
    "/media/",
)

class SitePasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if path.startswith(EXEMPT_PATHS):
            return self.get_response(request)

        if request.session.get("site_unlocked"):
            return self.get_response(request)

        return redirect("site_password")

