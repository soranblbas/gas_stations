from django.forms import HiddenInput

from .models import *
from django.contrib import admin
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.options import csrf_protect_m
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from django.core.exceptions import ValidationError


# class SalesItem(admin.TabularInline):
#     model = Sales
#     extra = 1
#
#
# @admin.register(S_Invoice)
# class ProfileAdmin(admin.ModelAdmin):
#     inlines = [SalesItem]
#
#     class Meta:
#         model = S_Invoice
#
#     list_display = ('invoice_number', 'total_sales_amount', 'get_station_numbers')
#
#     def get_station_numbers(self, obj):
#         return ", ".join(obj.get_station_numbers())
#
#     get_station_numbers.short_description = "Station Numbers"
class SalesAdminInline(admin.TabularInline):
    model = Sales
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "gas_station":
            if request.user.is_superuser:
                pass
            else:
                kwargs["queryset"] = GasStation.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(S_Invoice)
class S_InvoiceAdmin(admin.ModelAdmin):
    inlines = [SalesAdminInline]

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if request.method == 'POST':
            try:
                return super().changeform_view(request, object_id=object_id, form_url=form_url,
                                               extra_context=extra_context)
            except ValueError as error:
                self.message_user(request, _(str(error)), level='ERROR')
                url = reverse('admin:%s_%s_change' % (self.opts.app_label, self.opts.model_name), args=[object_id])
                return HttpResponseRedirect(url)
        else:
            return super().changeform_view(request, object_id=object_id, form_url=form_url, extra_context=extra_context)

    def show_sales_total(self, obj):
        total_sales = sum(sale.total_amount for sale in obj.sales.all())
        return format_html('<b>{}</b>', total_sales)

    def show_station_number(self, obj):
        station_number = obj.sales.first().gas_station.station if obj.sales.first() else '-'
        return format_html('<b>{}</b>', station_number)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(sales__gas_station__user=request.user)

    # def save_model(self, request, obj, form, change):
    #     if not change:
    #         obj.user = request.user
    #     obj.save()

    show_sales_total.short_description = _('Total Sales')
    show_station_number.short_description = _('Station Number')

    # list_display = ('invoice_number', 'show_sales_total', 'show_station_number')
    # search_fields = ('invoice_number', 'sales__gas_station__station_number')

    list_display = ('invoice_number', 'total_sales_amount', 'get_station_numbers', 'shift', 'sale_invoice_date',)
    readonly_fields = ('shift',)
    list_filter = ('shift', 'sale_invoice_date',)


#
#     def get_station_numbers(self, obj):
#         return ", ".join(obj.get_station_numbers())
#
#     get_station_numbers.short_description = "Station Numbers"
class StockItem(admin.TabularInline):
    model = Stock
    extra = 1

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(gas_station__user=request.user)


@admin.register(Stock_Invoice)
class ProfileAdmin(admin.ModelAdmin):
    inlines = [StockItem]

    class Meta:
        model = Stock_Invoice

    readonly_fields = ('total_amount',)

    # list_display = ('invoice_number', 'customer_name')


class GasStationAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


# class StockAdmin(admin.ModelAdmin):
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if request.user.is_superuser:
#             return qs
#         return qs.filter(gas_station__user=request.user)


class SalesAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(gas_station__user=request.user)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('total_amount',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

    class Meta:
        model = Order

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "gas_station":
            if request.user.is_superuser:
                pass
            else:
                kwargs["queryset"] = GasStation.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Show the status field only to users in the "Gas Station Managers" group
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj=obj)
        if obj is None:
            return [f for f in fields if f != 'status']
        elif request.user.groups.filter(name='Marketing').exists():
            return fields
        return [f for f in fields if f != 'status']

    list_display = ('invoice_number', 'shift', 'gas_station', 'status', 'created_at', 'updated_at',
                    'order_delivered',)
    readonly_fields = ('shift',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(gas_station__user=request.user)

    # Staff and admin fields permission


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'production_date', 'expire_date', 'days_until_expiry')
    readonly_fields = ('days_until_expiry',)

    def days_until_expiry(self, obj):
        try:
            today = date.today()
            delta = obj.expire_date - today
            days = delta.days
            if days <= 10:
                return format_html('<span style="color: red;">{}</span>', days)
            else:
                return days
        except:
            return date.today()

    days_until_expiry.short_description = 'Days until expiry'


@admin.register(station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(GasStation)
class GasStationAdmin(admin.ModelAdmin):
    list_display = ('address', 'city', 'state', 'zip_code',)


# @admin.register(Stock)
# class StockAdmin(admin.ModelAdmin):
#     list_display = ('stock_invoice', 'gas_station', 'item', 'quantity',)
#
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if request.user.is_superuser:
#             return qs
#         return qs.filter(gas_station__user=request.user)


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('gas_station', 'item', 'stock', 'sale', 'pur_qty', 'sale_qty', 'total_bal_qty',)
    list_filter = ('gas_station', 'item',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(gas_station__user=request.user)


# admin.site.register(GasStation, GasStationAdmin)
# admin.site.register(Sales, SalesAdmin)

admin.site.site_header = "Gas Station Portal"
admin.site.site_title = "Gas Station  Admin Portal"
admin.site.index_title = "Welcome to Gas Station  Portal"
