
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseNotFound
from datetime import datetime, timedelta
from pyexpat.errors import messages
from django.contrib import messages
from .filters import Sales_Filter
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


@login_required()
def sales_report(request):
    if request.user.groups.filter(
            name__in=['Admin', 'Finance', 'Marketing']).exists() or request.user.is_superuser:
        s_reports = Sales.objects.select_related()
        myFilter = Sales_Filter(request.GET, queryset=s_reports)
        s_reports = myFilter.qs
        context = {'s_reports': s_reports, 'myFilter': myFilter}
        return render(request, 'station/reports/sales_report.html', context)

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
        # Check if the request contains date filter parameters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Convert the date strings to datetime objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

        # Adjust the end date if it is the same as the start date
        if start_date and end_date and start_date == end_date:
            end_date += timedelta(days=1)

        # Filter the inventory items based on the date range
        st = Inventory.objects.all()
        if start_date and end_date:
            st = st.filter(stock__created_at__range=(start_date, end_date))

        context = {
            'st': st,
            'start_date': start_date_str,
            'end_date': end_date_str
        }

        return render(request, 'station/reports/stock_report.html', context)
    else:
        message = "You do not have permission to access this page."
        return render(request, 'station/reports/permission_denied.html', {'message': message})


@login_required()
def order_report(request):
    if request.user.groups.filter(
            name__in=['Admin', 'Marketing', 'Finance', 'Operation']).exists() or request.user.is_superuser:
        # Check if the request contains date filter parameters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Convert the date strings to datetime objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

        # Filter the orders based on the date range
        orders = OrderItem.objects.select_related('order', 'item')
        if start_date and end_date:
            orders = orders.filter(order__created_at__range=(start_date, end_date))

        return render(request, 'station/reports/orders_report.html', {'orders': orders, 'start_date': start_date_str, 'end_date': end_date_str})

    else:
        message = "You do not have permission to access this page."
        return render(request, 'station/reports/permission_denied.html', {'message': message})



@login_required()
def complted_order_report(request):
    if request.user.groups.filter(
            name__in=['Operation', 'Finance', 'Marketing']).exists() or request.user.is_superuser:
        orders = OrderItem.objects.select_related().filter(order__status='COMPLETED')
        return render(request, 'station/reports/completed_orders_report.html', {'orders': orders})

    else:
        message = "You do not have permission to access this page."
        return render(request, 'station/reports/permission_denied.html', {'message': message})


# orders = OrderItem.objects.select_related()
# return render(request, 'station/reports/orders_report.html', {'orders': orders})


@login_required()
def station_report(request):
    if request.user.groups.filter(
            name__in=['Admin', 'Marketing', 'Finance']).exists() or request.user.is_superuser:
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
def reports(request):

    return render(request, 'station/reports/reports.html')


def handler404(request, exception):
    return HttpResponseNotFound(render(request, 'station/404.html'))





