from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from .models import Product, Cart, Order, OrderItem 
from .forms import CheckoutForm # Import CheckoutForm
from tenant.models import Tenant
from django.contrib.auth.decorators import login_required 
from django.contrib import messages 
from django.db.models import Q 
from django.db import transaction # For atomic transactions


def home(request):
    # Display some products on the home page, e.g., first 3 by name
    # The 'featured' field was removed; using a simple slice for now.
    # The template iterates `product in articles`, so we pass `articles` as key.
    featured_products = Product.objects.all().order_by('name')[:3]
    
    dominTitle = request.get_host().split('.')[0]
    try:
        tenant_obj = Tenant.objects.get(blog_name=dominTitle)
        titleName = tenant_obj.blog_name
    except Tenant.DoesNotExist:
        titleName = 'My Shop' # Default title if tenant not found

    context = {
        'products': featured_products, # Changed context key to 'products'
        'title': titleName
    }
    return render(request, 'index.html', context)


def product_list(request): # Renamed from articles
    query = request.GET.get('query')
    if not query:
        query = ''

    # Search for query in product name or description
    products_qs = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    ).order_by('name')

    # Tags are removed as they are not part of Product model

    context = {
        'products': products_qs, # Changed context key to 'products'
        'title': 'All Products'
    }
    return render(request, 'articles.html', context) # Still uses articles.html template


def product_detail(request, pk): # Renamed from article, takes pk
    # The template uses `product.` for accessing fields.
    product_obj = get_object_or_404(Product, pk=pk)

    context = {
        'product': product_obj, # Template expects 'product'
        'title': product_obj.name
    }
    return render(request, 'article.html', context) # Still uses article.html template


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

    if not created:
        # If item already exists, increment quantity, check stock
        if product.stock > cart_item.quantity:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"{product.name} quantity updated in your cart.")
        else:
            messages.error(request, f"Not enough stock for {product.name}.")
    else:
        # If new item, check stock before adding
        if product.stock >= 1:
            cart_item.quantity = 1 # Already defaults to 1 by model, but explicit
            cart_item.save() # Save the new cart item
            messages.success(request, f"{product.name} added to your cart.")
        else:
            cart_item.delete() # Delete the cart item if stock is 0
            messages.error(request, f"Not enough stock for {product.name}.")
            # Redirect back to product page or wherever appropriate
            return redirect(request.META.get('HTTP_REFERER', 'blog:home'))


    return redirect('blog:view_cart')


@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f"{product_name} removed from your cart.")
    return redirect('blog:view_cart')


@login_required
def decrease_cart_item_quantity(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    product_name = cart_item.product.name
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        messages.success(request, f"Quantity of {product_name} decreased.")
    else:
        cart_item.delete()
        messages.success(request, f"{product_name} removed from your cart.")
    return redirect('blog:view_cart')


@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.subtotal for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'title': 'Your Shopping Cart'
    }
    return render(request, 'blog/cart.html', context)


@login_required
@transaction.atomic # Ensure all database operations in this view are atomic
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items:
        messages.error(request, "Your cart is empty. Please add items before checking out.")
        return redirect('blog:view_cart')

    total_price = sum(item.subtotal for item in cart_items)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Re-check cart and total price at the time of order submission
            current_cart_items = Cart.objects.filter(user=request.user)
            if not current_cart_items:
                messages.error(request, "Your cart became empty during checkout. Please try again.")
                return redirect('blog:view_cart')
            
            current_total_price = sum(item.subtotal for item in current_cart_items)

            order = form.save(commit=False)
            order.user = request.user
            order.total_price = current_total_price
            order.status = 'Pending' # Default status
            order.save()

            for item in current_cart_items:
                # Check stock one last time before creating OrderItem
                product = item.product
                if product.stock < item.quantity:
                    messages.error(request, f"Sorry, '{product.name}' is out of stock or quantity not available. Your order has not been placed.")
                    # Transaction will be rolled back due to returning without committing form.save() fully or other operations
                    # To be absolutely explicit, you could raise an IntegrityError or similar that transaction.atomic handles
                    return redirect('blog:view_cart') # Or checkout page to show the error

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=product.price # Price at the time of order
                )
                # Decrement stock
                product.stock -= item.quantity
                product.save()
            
            # Clear the cart
            current_cart_items.delete()

            messages.success(request, "Your order has been placed successfully!")
            return redirect('blog:order_confirmation', order_id=order.id)
        else:
            # Form is invalid, re-render with errors
            messages.error(request, "Please correct the errors below.")
    else: # GET request
        form = CheckoutForm()

    context = {
        'form': form,
        'cart_items': cart_items, # For display if needed, though typically summary is enough
        'total_price': total_price,
        'title': 'Checkout'
    }
    return render(request, 'blog/checkout.html', context)


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
        'title': f"Order #{order.id} Confirmed"
    }
    return render(request, 'blog/order_confirmation.html', context)
