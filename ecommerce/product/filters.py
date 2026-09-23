import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    keyword = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    brand = django_filters.CharFilter(field_name="brand", lookup_expr='icontains')
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    category = django_filters.CharFilter(field_name="category__slug", lookup_expr='iexact')
    category_id = django_filters.NumberFilter(field_name="category__id")
    min_rating = django_filters.NumberFilter(field_name="ratings_avg", lookup_expr='gte')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')

    class Meta:
        model = Product
        fields = ['keyword', 'brand', 'min_price', 'max_price', 'category', 'category_id', 'min_rating', 'in_stock']

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset