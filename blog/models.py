from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import DecimalField, IntegerField, PositiveIntegerField # Add IntegerField and PositiveIntegerField

from ckeditor_uploader.fields import RichTextUploadingField


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = RichTextUploadingField(null=True, blank=True) # Renamed from body
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(null=True, blank=True, upload_to="product_images/", default="placeholder.png") # Changed upload_to
    stock = models.IntegerField(default=0)

    # Removed author, headline, sub_headline, featured, tags, options, slug, publish, status, objects, articlemanager

    def get_absolute_url(self):
        # Assuming you have a URL pattern named 'product_detail' that takes a pk or slug
        # If using a slug, ensure you have a slug field in the model
        return reverse('blog:product_detail', args=[self.pk]) # Updated for product detail view by pk

    class Meta:
        ordering = ('name',) # Order by name

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} for {self.user.username}"

    @property
    def subtotal(self):
        return self.quantity * self.product.price


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Order {self.id} by {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2) # Price at the time of order
    created_at = models.DateTimeField(auto_now_add=True) # Keep track of when item was added

    def __str__(self):
        return f"{self.quantity} of {self.product.name} for Order {self.order.id}"

    @property
    def subtotal(self):
        return self.quantity * self.price
