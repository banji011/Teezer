from django.urls import path
from .views import *

app_name = 'core'

urlpatterns = [
    path('', homepage, name='home'),
    path('s/', search, name='search'),
    path('shop/', ShopView.as_view(), name='shop'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<slug>/',
         remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('add-single-item-from-cart/<slug>/',
         add_single_item_from_cart, name='add-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    # path('cart', cart, name='cart')
]
