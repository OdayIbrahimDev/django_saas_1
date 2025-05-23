from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='products'), # Renamed from 'articles' to 'products', view to 'product_list'
    path('product/<int:pk>/', views.product_detail, name='product_detail'), # View changed to 'product_detail'
    # Cart URLs
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'), 
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'), 
    path('cart/decrease/<int:cart_item_id>/', views.decrease_cart_item_quantity, name='decrease_cart_item_quantity'),
    # Checkout URLs
    path('checkout/', views.checkout, name='checkout'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
]
