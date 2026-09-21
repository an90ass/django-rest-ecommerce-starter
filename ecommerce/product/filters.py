import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    keyword = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    category = django_filters.CharFilter(field_name="category__name", lookup_expr='iexact')
    brand = django_filters.CharFilter(field_name="brand", lookup_expr='iexact')
    created_at = django_filters.DateFromToRangeFilter(field_name="created_at")
    class Meta:
        model = Product
        fields = ['keyword', 'min_price', 'max_price', 'category', 'brand', 'created_at']