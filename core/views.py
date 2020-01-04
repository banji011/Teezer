import string
import random
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import ListView, DetailView
from django.views import View
from django.utils import timezone
from .models import *
from .forms import *
import requests
from paystackapi.paystack import Paystack
paystack_secret_key = settings.PAYSTACK_SECRET_KEY


# Create your views here.


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


def search(request):
    try:
        q = request.GET.get('q')
    except:
        q = None

    if q:
        items = Item.objects.filter(name__icontains=q)
        context = {'query': q,
                   'items': items
                   }
        template = 'search_results.html'
    else:
        template = 'search_results.html'
        context = {}
    return render(request, template, context)


def homepage(request):
    sliders = Slider.objects.all_featured()
    banner = PremiumBanner.objects.get_featured_item()
    items = Item.objects.filter(category='TS').order_by('-id')[:4]
    hoody = Item.objects.filter(category='HO').order_by('-id')[:4]
    context = {
        'items': items,
        'hoody': hoody,
        'sliders': sliders,
        'banner': banner
    }
    return render(request, 'index.html', context)


class ShopView(ListView):
    model = Item
    paginate_by = 9
    template_name = 'shop.html'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(
                user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect('/')


class ProductDetailView(DetailView):
    model = Item
    template_name = "product-single.html"


# def productdetail(request, slug):

#     try:
#         context = {
#             'item': Item.objects.get(slug=slug)
#         }

#         return render(request, 'productsingle.html', context)
#     except:
#         raise Http404

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order item is in the order
        if order.item.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated!")
            return redirect("core:order-summary")
        else:
            order.item.add(order_item)
            messages.info(request, "This item was added to your cart !")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.item.add(order_item)
        messages.info(request, "This item was added to your cart !")
    return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    print(item)
    print(request.POST)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        print("YeaH")
        order = order_qs[0]
        # check if order item is in the order
        if order.item.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False)[0]
            order.item.remove(order_item)
            messages.info(request, "This item was removed from your cart !")
            return redirect("core:order-summary")
        else:
            # Add a message saying user doesnt contain the order item
            messages.info(request, "This item was not in your cart !")
            return redirect("core:product-detail", slug=slug)

    else:
        # Add a message saying user doesnt have an order
        messages.info(request, "You do not have an active order!")
        return redirect("core:product-detail", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    print(item)
    print(request.POST)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        print("YeaH")
        order = order_qs[0]
        # check if order item is in the order
        if order.item.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.item.remove(order_item)
            order_item.save()
            messages.info(request, "This item quantity was updated !")
            return redirect("core:order-summary")
        else:
            # Add a message saying user doesnt contain the order item
            messages.info(request, "This item was not in your cart !")
            return redirect("core:product-detail", slug=slug)

    else:
        # Add a message saying user doesnt have an order
        messages.info(request, "You do not have an active order!")
        return redirect("core:product-detail", slug=slug)


@login_required
def add_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    print(item)
    print(request.POST)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        print("YeaH")
        order = order_qs[0]
        # check if order item is in the order
        if order.item.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False)[0]
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated !")
            return redirect("core:order-summary")
        else:
            # Add a message saying user doesnt contain the order item
            messages.info(request, "This item was not in your cart !")
            return redirect("core:product-detail", slug=slug)

    else:
        # Add a message saying user doesnt have an order
        messages.info(request, "You do not have an active order!")
        return redirect("core:product-detail", slug=slug)


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order,
                'couponform': CouponForm(),
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update({
                    'default_shipping_address': shipping_address_qs[0]
                })

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update({
                    'default_billing_address': billing_address_qs[0]
                })

            return render(self.request, 'checkout.html', context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order !")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(
                user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print('Using the default shipping address!')
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True)
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip_code = form.cleaned_data.get(
                        'shipping_zip_code')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip_code]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip_code=shipping_zip_code,
                            address_type='S'
                        )
                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')

                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')
                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print('Using the default billing address!')
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True)
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip_code = form.cleaned_data.get(
                        'billing_zip_code')

                    if is_valid_form([billing_address1, billing_country, billing_zip_code]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip_code=billing_zip_code,
                            address_type='B'
                        )
                        billing_address.save()
                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')

                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()
                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'PS':
                    return redirect('core:payment', payment_option='paystack')
                elif payment_option == 'PP':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(
                        self.request, "Invalid Payment Option ")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect('core:order-summary')


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        amount = order.get_total() * 100
        if order.billing_address:
            context = {
                'order': order,
                'amount': amount,
                'DISPLAY_COUPON_FORM': False
            }
            return render(self.request, 'payment.html', context)
        else:
            messages.warning(
                self.request, "You have not added a billing address ")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        amount = order.get_total()
        reference = self.request.POST.get('paystackToken')
        print(reference)
        headers = {'Authorization': f'Bearer {paystack_secret_key}'}
        resp = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
        response = resp.json()
        try:
            status = response['data']['status']
            auth_code = response['data']['authorization']['authorization_code']
            if status == "success":
                # create payment
                payment = Payment()
                payment.paystack_charge_id = auth_code
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                order_items = order.item.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()
                messages.success(self.request, "Payment is successful !")
                return redirect('/')
            else:
                messages.warning(self.request, "Payment not successful")
                return redirect('/')
        except:
            messages.warning(self.request, "Payment not successful")
            return redirect('/')


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist !")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon !")
                return redirect("core:checkout")

            except ObjectDoesNotExist:
                messages.info(
                    self.request, "You do not have an active order !")
                return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, 'request_refund.html', context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()
                messages.info(self.request, "Your request was received")
                return redirect('core:request-refund')

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist")
                return redirect('core:request-refund')
