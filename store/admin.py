from django.contrib import admin
from .models import *


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ['slug', 'category_slug']


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'customer', 
        'ordered', 
        'being_delivered', 
        'received', 
        'refund_requested', 
        'refund_granted', 
        'shipping_address', 
        'coupon'
    ]
    list_display_links = [
        'customer',
        'shipping_address',
        'coupon'
    ]

    list_filter = [
        'customer', 
        'ordered', 
        'being_delivered',
        'received',
        'refund_requested',
        'refund_granted'
    ]

    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'customer',
        'province',
        'city',
        'zipcode',
        'address'
    ]
    search_fields = [
        'customer',
        'province',
        'city',
        'zipcode',
        'address'
    ]

admin.site.register(Customer)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Address, AddressAdmin)
admin.site.register(Coupon)
admin.site.register(Refund)