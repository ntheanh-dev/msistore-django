from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 100
    default_page_size = 100

    def get_page_size(self, request):
        # Get the page size from the query parameter or use the default
        page_size = request.query_params.get(self.page_size_query_param, self.default_page_size)

        try:
            # Try converting to an integer
            return min(int(page_size), self.max_page_size)
        except (TypeError, ValueError):
            # Handle the case where page_size is None or not a valid integer
            return self.default_page_size

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data['total_pages'] = self.page.paginator.num_pages
        return response

    def get_limit(self, request):
        # Get the limit from the query parameter or use the default
        limit = int(request.query_params.get('limit', self.max_page_size))

        # Ensure the limit is within a reasonable range
        return min(limit, self.max_page_size)

    def paginate_queryset(self, queryset, request, view=None):
        """
        Override paginate_queryset to apply both the limit and pagination to the queryset.
        """
        page_size = self.get_page_size(request)
        limit = self.get_limit(request)

        result = super().paginate_queryset(queryset, request, view=view)
        return result[:limit]  # Apply both pagination and limit