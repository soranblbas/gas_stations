from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('gas-station/', views.gas_station_detail, name='gas_station_detail'),
    path('stock/', views.stock_detail, name='stock_detail'),
    path('sales/', views.sales_detail, name='sales_detail'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
]
