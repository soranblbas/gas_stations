import django_filters
from django_filters import DateFilter
from .models import *


class Sales_Filter(django_filters.FilterSet):
    max_date = DateFilter(field_name='sale_date', lookup_expr='gte')
    min_date = DateFilter(field_name='sale_date', lookup_expr='lte')

    class Meta:
        model = Sales
        fields = ['min_date', 'max_date']
        exclude = ['sale_date', ]


# class Stock_Filter(django_filters.FilterSet):
#     max_date = DateFilter(field_name='created_at', lookup_expr='gte')
#     min_date = DateFilter(field_name='created_at', lookup_expr='lte')
#
#     class Meta:
#         model = Stock
#         fields = ['min_date', 'max_date']
#         exclude = ['created_at', ]
