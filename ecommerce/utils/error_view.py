from django.http import JsonResponse

def handle_404(request, exception):
    message = 'The requested resource was not found.'
    response = JsonResponse({'error': message})
    response.status_code = 404
    return response

def handle_500(request):
    
    message = 'An internal server error occurred.'
    response = JsonResponse({'error': message})
    response.status_code = 500
    return response



