from django.urls import path

from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
                  path('', home, name='home'),
                  # path('sales-report/', sales_report, name='sales_report'),
                  path('stock-report/', views.stock_report, name='stock_report'),
                  path('order-report/', order_report, name='order_report'),
                  path('station-report/', station_report, name='station_report'),
                  path('login', views.loginPage, name="login"),
                  path('logout', views.logoutUser, name="logout"),
                  path('sales_report', views.sales_report, name="sales_report"),
                  path('reports', views.reorts, name="reports"),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
