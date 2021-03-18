from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('products/', views.AllProductView.as_view(), name='all-product'),
    path('products/category/<category_slug>/', views.category, name='category'),
    path('product/detail/<slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/<slug>', views.add_to_cart, name='add-to-cart'),
    path('cart/remove-product/<slug>/', views.remove_from_cart, name='remove-from-cart'),
    path('cart/remove-single-product/<slug>/', views.remove_single_product_from_cart, name='remove-single-product'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('checkout/coupon/add/', views.AddCouponView.as_view(), name='add-coupon'),
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/order/detail/<id>/', views.order_detail, name='order-detail'),
    path('accounts/order/refund-request/<id>/', views.refund_request, name='refund-request')
]