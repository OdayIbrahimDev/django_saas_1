from django.contrib import admin
from .models import Product, Cart, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'id')
    search_fields = ('name', 'description')
    list_filter = ('price', 'stock')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'created_at')
    list_filter = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'product__name')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 # Don't show extra forms by default
    readonly_fields = ('product', 'quantity', 'price', 'subtotal') # Make fields read-only in inline view

    def subtotal(self, instance):
        return instance.subtotal
    subtotal.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'customer_name', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('id', 'customer_name', 'user__username')
    inlines = [OrderItemInline]
    readonly_fields = ('user', 'total_price', 'created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items__product')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'subtotal_display')
    list_filter = ('order__id', 'product')
    search_fields = ('order__id', 'product__name')
    readonly_fields = ('price',)

    def subtotal_display(self, obj):
        return obj.subtotal
    subtotal_display.short_description = 'Subtotal'

# To unregister any models if they were previously registered and are now removed (like Tag, Profile)
# This is more of a failsafe; ideally, the original registrations are just deleted as done above.
# from django.contrib.admin.sites import NotRegistered
# try:
#     admin.site.unregister(models.Tag)
# except NotRegistered:
#     pass

# try:
#     admin.site.unregister(models.Profile)
# except NotRegistered:
#     pass

# try:
#     # Assuming Article was registered directly or via a class that might not exist
#     # This part is tricky if the model itself (models.Article) is gone.
#     # If models.Article is deleted, this line itself would cause an AttributeError.
#     # It's better to just remove the old admin.site.register(models.Article) or @admin.register(models.Article)
#     pass
# except NotRegistered:
#     pass
