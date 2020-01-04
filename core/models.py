from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.utils import timezone

# Create your models here.

CATEGORY_CHOICES = (
    ('TS', 'T-Shirt'),
    ('HO', 'Hoodie'),
    ('HA', 'Hat')
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Item(models.Model):
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100, blank=True, null=True)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(
        choices=CATEGORY_CHOICES, max_length=2, default='TS')
    label = models.CharField(choices=LABEL_CHOICES, max_length=1, default='P')
    timestamp = models.DateTimeField(auto_now=True)
    slug = models.SlugField()
    description = models.TextField()
    stock = models.IntegerField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("core:product-detail", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })


class ItemImage(models.Model):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, blank=True, null=True)
    main_image = models.ImageField(
        upload_to='products/images/', blank=True, null=True)
    image1 = models.ImageField(
        upload_to='products/images/', blank=True, null=True)
    image2 = models.ImageField(
        upload_to='products/images/', blank=True, null=True)
    image3 = models.ImageField(
        upload_to='products/images/', blank=True, null=True)
    featured = models.BooleanField(default=False)
    thumbnail = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.item.name


class VariationManager(models.Manager):
    def sizes(self):

        return super(VariationManager, self).filter(category='size')

    def style(self):

        return super(VariationManager, self).filter(category='style')


VAR_CATEGORIES = (
    ('size', 'size'),
    ('style', 'style')
)


class ProductVariation(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    category = models.CharField(
        max_length=120, choices=VAR_CATEGORIES, default='size')
    title = models.CharField(max_length=50)  # size

    objects = VariationManager()

    def __str__(self):
        return f"Item => {self.item.name}. Variations => {self.category}: {self.title}"


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    item = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a billing address
    3. Failed Checkout
    4. Payment
    (Preprocessing, processing, packaging etc)
    5. Being delivered
    6. Received
    7. Refunds
    '''

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.item.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total


ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping')
)


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip_code = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    paystack_charge_id = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)


class MarketingQueryset(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True)\
            .filter(start_date__lt=timezone.now())\
            .filter(end_date__gte=timezone.now())


class MarketingManager(models.Manager):
    def get_queryset(self):
        return MarketingQueryset(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def all_featured(self):
        return self.get_queryset().active().featured()

    def get_featured_item(self):
        try:
            return self.get_queryset().active().featured()[0]
        except:
            return None

    def get_latest_featured_item(self):
        try:
            return self.get_queryset().active().featured().latest()
        except:
            return None


class Slider(models.Model):
    image = models.ImageField(upload_to='marketing/images/')
    order = models.IntegerField(default=0)
    url_link = models.CharField(max_length=250, null=True, blank=True)
    sub_heading = models.CharField(max_length=120, null=True, blank=True)
    side_heading = models.CharField(max_length=120, null=True, blank=True)
    header_text = models.CharField(max_length=120, null=True, blank=True)
    text = models.CharField(max_length=300, null=True, blank=True)
    active = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    start_date = models.DateTimeField(
        auto_now_add=False, auto_now=False, null=True, blank=True)
    end_date = models.DateTimeField(
        auto_now_add=False, auto_now=False, null=True, blank=True)

    objects = MarketingManager()

    def __str__(self):
        return self.header_text

    class Meta:
        ordering = ['order', '-start_date', '-end_date']


class PremiumBanner(models.Model):
    banner1 = models.ImageField(upload_to='marketing/premium/images/')
    banner2 = models.ImageField(upload_to='marketing/premium/images/')
    url_link1 = models.CharField(max_length=250, null=True, blank=True)
    url_link2 = models.CharField(max_length=250, null=True, blank=True)
    header_text1 = models.CharField(max_length=120, null=True, blank=True)
    header_text2 = models.CharField(max_length=120, null=True, blank=True)
    text1 = models.CharField(max_length=300, null=True, blank=True)
    text2 = models.CharField(max_length=300, null=True, blank=True)
    active = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    start_date = models.DateTimeField(
        auto_now_add=False, auto_now=False, null=True, blank=True)
    end_date = models.DateTimeField(
        auto_now_add=False, auto_now=False, null=True, blank=True)

    objects = MarketingManager()

    def __str__(self):
        return f"{self.header_text1} {self.header_text2}"

    # class Meta:
    #     ordering = ['-start_date', '-end_date']
