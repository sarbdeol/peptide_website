from django.db import models
from django.utils.text import slugify
from django.utils.timezone import now

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    price_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    short_description = models.CharField(max_length=300, blank=True)

    # 4 SECTIONS
    description = models.TextField(blank=True)
    coa_hplc_ms = models.TextField(blank=True, verbose_name="COA / HPLC / MS")
    third_party_testing = models.TextField(blank=True, verbose_name="3rd Party Testing")
    storage = models.TextField(blank=True)

    # SEO
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    seo_keywords = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        if not self.seo_title:
            self.seo_title = f"{self.name} Research Peptide | COA Verified"

        if not self.seo_description:
            self.seo_description = (
                f"{self.name} research peptide with verified purity and COA documentation."
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to="products/",
        help_text="Upload vial, label, or packaging image"
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Main product image"
    )

    def __str__(self):
        return f"{self.product.name} image"

class TempCart(models.Model):
    created_at = models.DateTimeField(default=now)
    data = models.JSONField()

    def __str__(self):
        return f"TempCart #{self.id}"
    
class Order(models.Model):
    created_at = models.DateTimeField(default=now)
    items = models.JSONField()
    amount_total = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    status = models.CharField(max_length=30, default="Pending")
    payment_method = models.CharField(max_length=30, default="crypto")

    def __str__(self):
        return f"Order #{self.id}"