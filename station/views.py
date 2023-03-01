from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import GasStationForm
from .models import *


def home(request):
    if request.user.is_authenticated:
        return redirect('station/gas_station_detail')
    else:
        return render(request, 'station/home.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        gas_station_form = GasStationForm(request.POST)
        if form.is_valid() and gas_station_form.is_valid():
            user = form.save()
            gas_station = gas_station_form.save(commit=False)
            gas_station.user = user
            gas_station.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('station/gas_station_detail')
    else:
        form = UserCreationForm()
        gas_station_form = GasStationForm()
    return render(request, 'station/signup.html', {'form': form, 'gas_station_form': gas_station_form})


@login_required
def gas_station_detail(request):
    gas_station = GasStation.objects.get(user=request.user)
    return render(request, 'station/gas_station_detail.html', {'gas_station': gas_station})


@login_required
def stock_detail(request):
    gas_station = GasStation.objects.get(user=request.user)
    stock = Stock.objects.filter(gas_station=gas_station)
    return render(request, 'station/stock_detail.html', {'stock': stock})


@login_required
def sales_detail(request):
    gas_station = GasStation.objects.get(user=request.user)
    sales = Sales.objects.filter(gas_station=gas_station)
    return render(request, 'station/sales_detail.html', {'sales': sales})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('gas_station_detail')
        else:
            return render(request, 'station/login.html', {'error_message': 'Invalid login'})
    else:
        return render(request, 'station/login.html')


def user_logout(request):
    logout(request)
    return redirect('station/home')
