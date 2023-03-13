import secrets
from datetime import date, timezone
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
import uuid


class station(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class GasStation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    station = models.ForeignKey(station, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)

    def __str__(self):
        return str(self.station)


class Item(models.Model):
    name = models.CharField(max_length=255)
    price = models.PositiveIntegerField(default=1)
    production_date = models.DateField()
    expire_date = models.DateField()

    def __str__(self):
        return f"{self.name} - {self.price}"

    def days_until_expiry(self):
        today = date.today()
        delta = self.expire_date - today
        return delta.days


class Stock_Invoice(models.Model):
    invoice_number = models.CharField(max_length=8, unique=True, editable=False)

    def __str__(self):
        return f"{self.invoice_number}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate a random 8 character invoice number
            self.invoice_number = secrets.token_hex(4).upper()

        super().save(*args, **kwargs)


class Stock(models.Model):
    stock_invoice = models.ForeignKey(Stock_Invoice, on_delete=models.CASCADE, related_name='sales')
    gas_station = models.ForeignKey(GasStation, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.gas_station.station.name} - {self.item.name} - {self.quantity}"

    def save(self, *args, **kwargs):

        super(Stock, self).save(*args, **kwargs)

        ####
        inventory = Inventory.objects.filter(gas_station=self.gas_station, item=self.item).order_by('-id').first()

        if inventory:
            totalBal = inventory.total_bal_qty + self.quantity
        else:
            totalBal = self.quantity

        Inventory.objects.create(
            gas_station=self.gas_station,
            item=self.item,
            stock=self.stock_invoice,
            sale=None,
            pur_qty=self.quantity,
            sale_qty=None,
            total_bal_qty=totalBal
        )


class S_Invoice(models.Model):
    invoice_number = models.CharField(max_length=8, unique=True, editable=False)
    shift = models.CharField(max_length=20, blank=True, null=True)
    sale_invoice_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate a random 8 character invoice number
            self.invoice_number = secrets.token_hex(4).upper()

        if not self.shift:
            now = timezone.now()
            if now.hour >= 8 and now.hour < 4:
                self.shift = 'morning'
            elif now.hour >= 4 and now.hour < 12:
                self.shift = 'afternoon'
            else:
                self.shift = 'evening'

        super().save(*args, **kwargs)

    def __str__(self):
        return f" Invoice Number : {self.invoice_number}"

    def total_sales_amount(self):
        total_sales_amount = self.sales.aggregate(total=Sum('total_amount'))['total']
        return total_sales_amount or 0

    def get_station_numbers(self):
        station_numbers = [sale.gas_station.station for sale in self.sales.all()]
        print(f"station_numbers: {station_numbers}")
        station_numbers = list(set(station_numbers))
        print(f"station_numbers (unique): {station_numbers}")
        station_numbers = [str(station) for station in station_numbers]
        print(f"station_numbers (as strings): {station_numbers}")
        return ", ".join(station_numbers)

    get_station_numbers.short_description = "Station Numbers"


class Sales(models.Model):
    sales_invoice = models.ForeignKey(S_Invoice, on_delete=models.CASCADE, related_name='sales')
    gas_station = models.ForeignKey(GasStation, on_delete=models.CASCADE, related_name='sales')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0, editable=False)
    sale_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.gas_station.station.name} - {self.item.name} - {self.quantity} - {self.total_amount}"

    def save(self, *args, **kwargs):
        self.total_amount = self.item.price * self.quantity
        super().save(*args, **kwargs)
        try:
            inventory = Inventory.objects.filter(item=self.item, gas_station=self.gas_station).latest('id')
        except Inventory.DoesNotExist:
            raise ValueError(f"{self.item.name} is not in stock for station {self.gas_station.station.name}")

        totalBal = inventory.total_bal_qty
        if self.quantity > totalBal:
            raise ValueError(
                f"Sorry, we don't have enough {self.item.name} in stock for station {self.gas_station.station.name} right now. "
                f"Please reduce your sale quantity to {totalBal} or less."
            )

        inventory = Inventory.objects.filter(gas_station=self.gas_station, item=self.item).order_by('-id').first()
        if inventory:
            totalBal = inventory.total_bal_qty - self.quantity
        else:
            totalBal = 0

        Inventory.objects.create(
            gas_station=self.gas_station,
            item=self.item,
            stock=None,
            sale=self.sales_invoice,
            pur_qty=None,
            sale_qty=self.quantity,
            total_bal_qty=totalBal
        )

        #
        # # Update the stock quantity
        # stock.quantity -= self.quantity
        # stock.save()


class Order(models.Model):
    PN = 'PENDING'
    PR = 'PROCESSED'
    CM = 'COMPLETED'

    STATUS_CHOICES = (
        (PN, 'Pending'),
        (PR, 'processed'),
        (CM, 'Completed'),
    )
    invoice_number = models.CharField(max_length=10, unique=True, editable=False)
    gas_station = models.ForeignKey(GasStation, on_delete=models.CASCADE)
    shift = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Order {self.id} ({self.get_status_display()}) by {self.gas_station.user}"

    # Make the status field visible only to superusers
    def status_visible_to(self, user):
        return user.is_superuser

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate a random 8 character invoice number
            self.invoice_number = secrets.token_hex(4).upper()

            if not self.shift:
                now = timezone.now()
                if now.hour >= 6 and now.hour < 14:
                    self.shift = 'morning'
                elif now.hour >= 14 and now.hour < 22:
                    self.shift = 'afternoon'
                else:
                    self.shift = 'evening'

        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.item.name} - {self.quantity}"


# Inventories
class Inventory(models.Model):
    gas_station = models.ForeignKey(GasStation, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock_Invoice, on_delete=models.CASCADE, default=0, null=True)
    sale = models.ForeignKey(S_Invoice, on_delete=models.CASCADE, default=0, null=True)
    pur_qty = models.FloatField(default=0, null=True)
    sale_qty = models.FloatField(default=0, null=True)
    total_bal_qty = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = 'Stock Details'

    def __str__(self):
        return str(self.item)
