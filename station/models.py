from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


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

    def __str__(self):
        return self.name


class Stock_Invoice(models.Model):
    invoice_number = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.invoice_number}"


class Stock(models.Model):
    stock_invoice = models.ForeignKey(Stock_Invoice, on_delete=models.CASCADE, related_name='sales')
    gas_station = models.ForeignKey(GasStation, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.gas_station.station.name} - {self.item.name} - {self.quantity}"


class S_Invoice(models.Model):
    invoice_number = models.CharField(max_length=255)

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
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    total_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    date = models.DateField()

    def __str__(self):
        return f"{self.gas_station.station.name} - {self.item.name} - {self.quantity} - {self.total_amount}"

    def save(self, *args, **kwargs):
        try:
            stock = Stock.objects.get(gas_station=self.gas_station, item=self.item)
        except Stock.DoesNotExist:
            raise ValueError(f"{self.item.name} is not in stock for station  {self.gas_station.station.name}")

        if self.quantity > stock.quantity:
            raise ValueError(
                f"Sorry, we don't have enough {self.item.name} in stock  for station   {self.gas_station.station.name} right now. "
                f"Please reduce your order quantity to {stock.quantity} or less."
            )

        self.total_amount = self.price * self.quantity
        super().save(*args, **kwargs)

        # Update the stock quantity
        stock.quantity -= self.quantity
        stock.save()
