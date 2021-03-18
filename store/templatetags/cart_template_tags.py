from django import template
from store.models import Order

register = template.Library()

@register.filter
def cart_product_count(customer):
    if customer.is_authenticated:
        order = Order.objects.filter(customer=customer, ordered=False)

        if order.exists():
            return order[0].product.count()
    return 0