from rest_framework.pagination import PageNumberPagination

class StandardPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 100

def get_paginated_response(request, queryset, serializer_class, pagination_class=StandardPagination):

    paginator = pagination_class()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = serializer_class(paginated_queryset, many=True)

    return paginator.get_paginated_response(serializer.data,)