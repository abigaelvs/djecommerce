from django.db import models
from django.utils.text import slugify
from django.shortcuts import reverse
from django.contrib.auth.models import User
from django.conf import settings

# django signals
from django.db.models.signals import post_save
from django.dispatch import receiver

# django ckeditor
from ckeditor.fields import RichTextField

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile/', blank=True, null=True)
    phone = models.CharField(max_length=13, blank=True, null=True)

    def __str__(self):
        return self.user.username

    @property
    def image_url(self):
        try:
            url = self.profile_pic.url
        except:
            url = '/static/img/no_user.jpg'
        return url

# signal for Customer model
# when created new user, django will automatically created customer model with new user
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.customer.save()


class Product(models.Model):
    name = models.CharField(max_length=30)
    price = models.DecimalField(decimal_places=0, max_digits=10)
    discount_price = models.DecimalField(decimal_places=0, max_digits=10, blank=True, null=True)
    image = models.ImageField(upload_to='product/', blank=True, null=True)
    category = models.CharField(max_length=30)
    description = RichTextField()
    date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField()
    category_slug = models.SlugField(blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        try:
            url = self.image.url
        except:
            url = '/static/img/no_product.png'
        return url

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.category_slug = slugify(self.category)
        super(Product, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:product-detail', kwargs={
            'slug': self.slug,
        })
    
    def get_add_to_cart_url(self):
        return reverse('store:add-to-cart', kwargs={
            'slug': slug
        })
    
    def get_remove_from_cart_url(self):
        return reverse('store:remove-from-cart', kwargs={
            'slug': slug
        })


class OrderItem(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)

    quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.customer.username

    def get_total_item_price(self):
        return self.quantity * self.product.price
    
    def get_total_discount_item_price(self):
        return self.quantity * self.product.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()
    
    def get_final_price(self):
        if self.product.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ManyToManyField(OrderItem)

    # the time when the order was created
    # when customer first time add their order item to the cart
    start_date = models.DateTimeField(auto_now=True)

    # the time when customer submit the order
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    shipping_address = models.ForeignKey('Address', blank=True, null=True, on_delete=models.SET_NULL)

    coupon = models.ForeignKey('Coupon', blank=True, null=True, on_delete=models.SET_NULL)

    # tracking the order
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    transaction_id = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.customer.username

    def get_total(self):
        total = 0
        for order_item in self.product.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total



class Address(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.TextField()
    province = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    zipcode = models.CharField(max_length=30)

    default = models.BooleanField(default=False)
    
    def __str__(self):
        return self.customer.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.order.customer.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.DecimalField(decimal_places=0, max_digits=10)

    def __str__(self):
        return self.code


