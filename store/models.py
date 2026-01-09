from django.db import models
from django.utils.timezone import now


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products/")

    def __str__(self):
        return f"Image for {self.product.name}"


class Order(models.Model):
    created_at = models.DateTimeField(default=now)
    items = models.JSONField()
    amount_total = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    status = models.CharField(max_length=30, default="Pending")
    payment_method = models.CharField(max_length=30, default="crypto")

    def __str__(self):
        return f"Order #{self.id}"
