from django.urls import path

from . import views
from .views import *
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', home, name='home'),
    path('sales-report/', sales_report, name='sales_report'),
    path('stock-report/', stock_report, name='stock_report'),
    path('order-report/', order_report, name='order_report'),
    path('station-report/', station_report, name='station_report'),
    path('login', views.loginPage, name="login"),
    path('logout', views.logoutUser, name="logout"),

]
