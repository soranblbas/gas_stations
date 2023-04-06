from multiprocessing import Value
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission
from django.db.models.functions import Coalesce
from django.forms import IntegerField
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.db.models import Sum, Case, When, F, Max
from django.views.generic import TemplateView
from pyexpat.errors import messages
from django.contrib import messages
from .filters import Sales_Filter
from .models import *
from django.views.generic import ListView
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


@login_required()
def sales_report(request):
    if request.user.groups.filter(
            name__in=['Admin', 'Operation', 'Finance', 'Marketing']).exists() or request.user.is_superuser:
        s_reports = Sales.objects.select_related()
        myFilter = Sales_Filter(request.GET, queryset=s_reports)
        s_reports = myFilter.qs
        context = {'s_reports': s_reports, 'myFilter': myFilter}
        return render(request, 'station/reports/sales_report.html', {'s_reports': s_reports})

    else:
        # show a message pop-up and redirect to the home page
        message = "You do not have permission to access this page."
        return render(request, 'station/reports/permission_denied.html', {'message': message})

    # s_reports = Sales.objects.select_related()
    # myFilter = Sales_Filter(request.GET, queryset=s_reports)
    # s_reports = myFilter.qs
    #
    # context = {'s_reports': s_reports, 'myFilter': myFilter}
    # return render(request, 'station/reports/sales_report.html', context)


@login_required()
def stock_report(request):
    if request.user.groups.filter(
            name__in=['Admin', 'Operation', 'Marketing', 'Finance']).exists() or request.user.is_superuser:
        st = Inventory.objects.all()

        context = {'st': st}

        return render(request, 'station/reports/stock_report.html', context)

    else:
        message = "You do not have permission to access this page."
        return render(request, 'station/reports/permission_denied.html', {'message': message})
    # st = Inventory.objects.all()
    # # st = Inventory.objects.values('item').annotate(last_bal_qty=MIN('total_bal_qty')).order_by('-id')
    #
    # context = {'st': st}
    #
    # return render(request, 'station/reports/stock_report.html', context)


@login_required()
def order_report(request):
    if request.user.groups.filter(
            name__in=['Admin', 'Operation', 'Marketing']).exists() or request.user.is_superuser:
        orders = OrderItem.objects.select_related()
        return render(request, 'station/reports/orders_report.html', {'orders': orders})

    else:
        message = "You do not have permission to access this page."
        return render(request, 'station/reports/permission_denied.html', {'message': message})


# orders = OrderItem.objects.select_related()
# return render(request, 'station/reports/orders_report.html', {'orders': orders})


@login_required()
def station_report(request):
    if request.user.groups.filter(
            name__in=['Admin', 'Operation', 'Marketing']).exists() or request.user.is_superuser:
        stations = GasStation.objects.all()
        sales = []
        for station in stations:
            station_sales = Sales.objects.filter(gas_station=station)
            total_sales = station_sales.aggregate(total=Sum('total_amount'))['total']
            sales.append({'station': station, 'total_sales': total_sales})
        return render(request, 'station/reports/station_report.html', {'sales': sales})

    else:
        message = "You do not have permission to access this page."
        return render(request, 'station/reports/permission_denied.html', {'message': message})


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


@login_required()
def shift_sale_report(request):
    # get all the sales
    sales = Sales.objects.all()
    context = {'sales': sales}
    # render the template with the shift-wise sales data
    return render(request, 'station/reports/sales_report.html', context)


@login_required()
def reorts(request):
    # get all the sales
    # sales = Sales.objects.all()
    # context = {'sales': sales}
    # # render the template with the shift-wise sales data
    return render(request, 'station/reports/reports.html')


def handler404(request, exception):
    return HttpResponseNotFound(render(request, 'station/404.html'))
#
#
# def item_stock(request):
#     item_stock_qs = Stock.objects.all().select_related('item', 'gas_station').order_by('item__name',
#                                                                                        'gas_station__name',
#                                                                                        '-datetime')
#     item_stock_dict = {}
#     for item_stock in item_stock_qs:
#         item_name = item_stock.item.name
#         station_name = item_stock.station.name
#         if item_name not in item_stock_dict:
#             item_stock_dict[item_name] = {}
#         if station_name not in item_stock_dict[item_name]:
#             item_stock_dict[item_name][station_name] = {
#                 'first_entry_balance': item_stock.quantity,
#                 'current_stock': item_stock.quantity,
#                 'total_sold': 0,
#             }
#         else:
#             item_stock_dict[item_name][station_name]['current_stock'] += item_stock.quantity
#         station = item_stock_dict[item_name][station_name]
#     context = {'item_stock_dict': item_stock_dict}
#     return render(request, 'station/reports/item_stock.html', context)
