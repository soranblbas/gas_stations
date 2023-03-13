from multiprocessing import Value
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required

from django.forms import IntegerField
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.db.models import Sum, Case, When, F, Max
from django.views.generic import TemplateView
from pyexpat.errors import messages

from .models import *

from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout


def home(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
    else:
        form = AuthenticationForm()

    if request.user.is_authenticated:
        return render(request, 'station/home.html')
    else:
        return render(request, 'station/login.html', {'form': form})


def sales_report(request):
    # get all the sales
    sales = Sales.objects.all()
    context = {'sales': sales}
    # render the template with the shift-wise sales data
    return render(request, 'station/reports/sales_report.html', context)


def stock_report(request):
    st = Inventory.objects.all()
    # st = Inventory.objects.values('item').annotate(last_bal_qty=MIN('total_bal_qty')).order_by('-id')

    context = {'st': st}

    return render(request, 'station/reports/stock_report.html', context)


def order_report(request):
    orders = OrderItem.objects.all()
    return render(request, 'station/reports/orders_report.html', {'orders': orders})


def station_report(request):
    stations = GasStation.objects.all()
    sales = []
    for station in stations:
        station_sales = Sales.objects.filter(gas_station=station)
        total_sales = station_sales.aggregate(total=Sum('total_amount'))['total']
        sales.append({'station': station, 'total_sales': total_sales})
    return render(request, 'station/reports/station_report.html', {'sales': sales})


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.info(request, 'Username Or Password is Incorrect')
                return render(request, 'station/login.html')
        context = {}
        return render(request, 'station/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def shift_sale_report(request):
    # get all the sales
    sales = Sales.objects.all()
    context = {'sales': sales}
    # render the template with the shift-wise sales data
    return render(request, 'station/reports/sales_report.html', context)


def reorts(request):
    # get all the sales
    # sales = Sales.objects.all()
    # context = {'sales': sales}
    # # render the template with the shift-wise sales data
    return render(request, 'station/reports/reports.html')


def handler404(request, exception):
    return HttpResponseNotFound(render(request, 'station/404.html'))
