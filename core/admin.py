from django.contrib import admin
from .models import *

# Register your models here.


# class ItemVariationAdmin(admin.ModelAdmin):
#     list_display = ['variation',
#                     'value']
#     list_filter = ['variation', 'variation__item']
#     search_fields = ['value']


# class ItemVariationInlineAdmin(admin.TabularInline):
#     model = ItemVariation
#     extra = 1

def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update order to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    'billing_address',
                    'shipping_address',
                    'payment',
                    'coupon']

    list_display_links = ['user',
                          'billing_address',
                          'shipping_address',
                          'payment',
                          'coupon']

    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted']
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip_code',
        'address_type',
        'default'
    ]
    list_filter = [
        'default',
        'address_type',
        'country'
    ]
    search_fields = [
        'user',
        'street_address',
        'apartment_address',
        'zip_code'
    ]


class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'author',
        'price',
        'discount_price',
        'category',
        'description'
    ]
    list_filter = [
        'author',
        'category'
    ]
    search_fields = [
        'name',
        'author',
        'category'
    ]
    date_hierarchy = 'timestamp'


class SliderAdmin(admin.ModelAdmin):
    list_display = ["order", "start_date", "end_date",
                    "active", "featured", "header_text"]
    list_filter = ["featured", "start_date", "end_date"]


class PremiumBannerAdmin(admin.ModelAdmin):
    list_display = ["start_date", "end_date",
                    "active", "featured", "header_text1", "header_text2"]
    list_filter = ["featured", "start_date", "end_date"]


admin.site.register(Item, ItemAdmin)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment)
admin.site.register(ProductVariation)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(UserProfile)
admin.site.register(ItemImage)
admin.site.register(Slider, SliderAdmin)
admin.site.register(PremiumBanner, PremiumBannerAdmin)
# admin.site.register(ItemVariation, ItemVariationAdmin)
# admin.site.register(Variation, VariationAdmin)
