from .models import *
from django.contrib import admin

from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.options import csrf_protect_m
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


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

    show_sales_total.short_description = _('Total Sales')
    show_station_number.short_description = _('Station Number')

    # list_display = ('invoice_number', 'show_sales_total', 'show_station_number')
    # search_fields = ('invoice_number', 'sales__gas_station__station_number')

    list_display = ('invoice_number', 'total_sales_amount', 'get_station_numbers')


#
#     def get_station_numbers(self, obj):
#         return ", ".join(obj.get_station_numbers())
#
#     get_station_numbers.short_description = "Station Numbers"
class StockItem(admin.TabularInline):
    model = Stock
    extra = 1


@admin.register(Stock_Invoice)
class ProfileAdmin(admin.ModelAdmin):
    inlines = [StockItem]

    class Meta:
        model = Stock_Invoice

    # list_display = ('invoice_number', 'customer_name')


class GasStationAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


class StockAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(gas_station__user=request.user)


class SalesAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "gas_station":
            # Show only the gas station associated with the current user
            gas_station = GasStation.objects.filter(user=request.user).first()
            if gas_station:
                kwargs["queryset"] = GasStation.objects.filter(pk=gas_station.station.pk)
            else:
                kwargs["queryset"] = GasStation.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "gas_station":
            if request.user.is_superuser:
                pass
            else:
                kwargs["queryset"] = GasStation.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(GasStation, GasStationAdmin)
admin.site.register(Item)
admin.site.register(Stock, StockAdmin)
admin.site.register(Sales, SalesAdmin)
admin.site.register(station)
