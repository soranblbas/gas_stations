from .models import *
from django.contrib import admin


class SalesItem(admin.TabularInline):
    model = Sales
    extra = 1


@admin.register(S_Invoice)
class ProfileAdmin(admin.ModelAdmin):
    inlines = [SalesItem]

    class Meta:
        model = S_Invoice

    # list_display = ('invoice_number', 'customer_name')


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


admin.site.register(GasStation, GasStationAdmin)
admin.site.register(Item)
admin.site.register(Stock, StockAdmin)
admin.site.register(Sales, SalesAdmin)
admin.site.register(station)
