from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.models import User

# django views
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages

# same app import
from .models import Product, Order, OrderItem, Address, Coupon, Customer, Refund
from .forms import CheckoutForm, CouponForm, RefundForm

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import datetime

from django.utils.text import slugify


class HomeView(View):
    def get(self, *args, **kwargs):
        product_list = Product.objects.all()
        categories = Product.objects.values('category').distinct()
        search_input = self.request.GET.get('search-area')

        for category in categories:
            category['category_slug'] = slugify(category['category'])
            
        if search_input:
            products = Product.objects.filter(name__icontains=search_input)
        else:
            products = Product.objects.all()
            search_input = ''
        
        context = {
            'products': products,
            'categories': categories,
            'search_input': search_input
        }
        return render(self.request, 'store/home-page.html', context)


class AllProductView(View):
    def get(self, *args, **kwargs):
        products = Product.objects.all()
        categories = Product.objects.values('category').distinct()
        search_input = self.request.GET.get('search-area')

        for category in categories:
            category['category_slug'] = slugify(category['category'])

        if search_input:
            products = Product.objects.filter(name__icontains=search_input)
        else:
            products = Product.objects.all()
            search_input = ''
        
        context = {
            'products': products,
            'categories': categories,
            'search_input': search_input
        }
        return render(self.request, 'store/all-product.html', context)

def category(request, category_slug):
    products = Product.objects.filter(category_slug=category_slug)
    categories = Product.objects.values('category').distinct()

    for category in categories:
        category['category_slug'] = slugify(category['category'])

    search_input = request.GET.get('search-area')
    search_input = ''

    
    context = {
            'products': products,
            'categories': categories,
            'search_input': search_input
    }
    return render(request, 'store/category.html', context)

class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product-detail.html'


class CartView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(customer=self.request.user, ordered=False)
            
            return render(self.request, 'store/cart.html', {'object': order})
        except ObjectDoesNotExist:
            messages.warning(
                self.request, 'You do not have an active order for now'
            )
            return redirect('store:home')


@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        product=product, customer=request.user, ordered=False
    )
    order_qs = Order.objects.filter(customer=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        # check if the order item is in the order
        if order.product.filter(product__slug=product.slug).exists():
            order_item.quantity += 1
            order_item.save()
        else:
            order.product.add(order_item)
            response = HttpResponse('cart', order.product.add(order_item))
            messages.info(request, 'This item was added to your cart.')
            return redirect('store:cart')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(customer=request.user, ordered_date=ordered_date)
        order.product.add(order_item)
        messages.info(request, 'This item was added to your cart.')
    return redirect('store:cart')


@login_required
def remove_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(customer=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        # check if the order item is in the order
        if order.product.filter(product__slug=product.slug).exists():
            order_item = OrderItem.objects.filter(
                product=product, customer=request.user, ordered=False
            )[0]
            order.product.remove(order_item)
            messages.info(request, 'This item was removed from your cart')
            return redirect('store:cart')
        else:
            messages.info(request, 'This item was not in your cart')
            return redirect('store:cart')
    else:
        messages.info(request, 'You do not have an active order')
        return redirect('store:cart')


@login_required
def remove_single_product_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(customer=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        # check if the item is in the order
        if order.product.filter(product__slug=product.slug).exists():
            order_item = OrderItem.objects.filter(
                product=product, customer=request.user, ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.product.remove(order_item)
            messages.info(request, 'This item quantity was added')
            return redirect('store:cart')
        else:
            messages.info(request, 'This item was not in your cart')
            return redirect('store:cart')
    else:
        messages.info(request, 'You do now have an active order')
        return redirect('store:cart')


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(customer=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order,
                'couponform': CouponForm(),
                'DISPLAY_COUPON_FORM': True,
            }
            shipping_address_qs = Address.objects.filter(
                customer=self.request.user,
                default=True,
            )

            if shipping_address_qs.exists():
                context.update({
                    'default_address': shipping_address_qs[0]
                })

            return render(self.request, 'store/checkout.html', context)
        except ObjectDoesNotExist:
            return redirect('store:store')
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)

        try:
            order = Order.objects.get(customer=self.request.user, ordered=False)

            if form.is_valid():

                # Shipping Address
                use_default_address = form.cleaned_data.get('use_default_address')
                print(use_default_address)
                if use_default_address:
                    address_qs = Address.objects.filter(
                        customer=self.request.user,
                        default=True,
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.ordered = True
                        order.save()
                    else:
                        messages.info(self.request, 'No default address available')
                        return redirect('store:checkout')
                    messages.success(self.request, 'Checkout successfull')
                    return redirect('store:home')
                else:
                    province = form.cleaned_data.get('province')
                    city = form.cleaned_data.get('city')
                    address = form.cleaned_data.get('address')
                    zipcode = form.cleaned_data.get('zipcode')

                    if is_valid_form([province, city, address, zipcode]):

                        address = Address(
                            customer=self.request.user,
                            city=city,
                            province=province,
                            address=address,
                            zipcode=zipcode,
                        )
                        

                        address.save()

                        order.shipping_address = address
                        order.ordered = True
                        order.transaction_id = datetime.now().timestamp()
                        order.save()

                        set_default_address = form.cleaned_data.get('set_default_address')
                        if set_default_address:
                            address.default = True    
                            address.save()

                        messages.success(self.request, 'Checkout Successful')
                        return redirect('store:home')
        except ObjectDoesNotExist:
           messages.warning(
               self.request, 'You do not have an active order for now'
           ) 
           return redirect('store:checkout')
            

def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, 'This coupon is not longer exist')
        return redirect('store:checkout')


class AddCouponView(View):
    def post(self, *args, **kwagrs):
        form = CouponForm(self.request.POST or None)

        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')

                order = Order.objects.get(
                    customer=self.request.user, ordered=False
                )
                order.coupon = get_coupon(self.request, code)
                order.save()

                messages.success(self.request, 'Successfully added coupon')
                return redirect('store:checkout')

            except ObjectDoesNotExist:
                messages.info(self.request, 'You do not have an active order')
                return redirect('store:checkout')
        else:
            messages.info(self.request, 'Invalid Coupon')
            return redirect('store:checkout')


@login_required
def profile(request):
    customer = Customer.objects.get(user=request.user)
    orders = Order.objects.filter(customer=request.user, ordered=True).order_by('-ordered_date')
    context = {
        'customer': customer,
        'orders': orders,
    }
    return render(request, 'store/profile.html', context)


@login_required
def order_detail(request, id):
    order = Order.objects.get(id=id)
    address = Address.objects.get(order=order)
    refund_qs = Refund.objects.filter(order=order)
    context = {
        'order': order,
        'address': address,
        'refund_qs': refund_qs
    }
    return render(request, 'store/order-detail.html', context)


@login_required
def refund_request(request, id):
    order = Order.objects.get(id=id)
    form = RefundForm()

    if request.method == 'POST':
        form = RefundForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data.get('reason')
            refund = Refund(
                order=order,
                reason=reason
            )
            refund.save()
            order.refund_requested = True
            order.save()

            messages.success(request, 'Refund request successfully submitted')
            return redirect('store:profile')
    context = {
            'order': order,
            'form': form,
    }
    return render(request, 'store/refund_request.html', context)