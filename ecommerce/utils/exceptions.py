from rest_framework.views import exception_handler
from django.utils.timezone import now

def custom_exception_handler(exc, context):

   # Custom exception handler for Django REST Framework to enforce enterprise standard error responses.

    response = exception_handler(exc, context)

    if response is not None:
        error_details = response.data
        message = "An error occurred while processing your request."
        
        if isinstance(error_details, dict):
            if "detail" in error_details:
                message = str(error_details.pop("detail"))
            elif "non_field_errors" in error_details:
                message = " ".join([str(e) for e in error_details.get("non_field_errors")])
        elif isinstance(error_details, list):
            message = " ".join([str(e) for e in error_details])

        custom_data = {
            "success": False,
            "error": {
                "code": exc.__class__.__name__,
                "message": message,
                "details": error_details if isinstance(error_details, (dict, list)) else {"detail": str(error_details)}
            },
            "timestamp": now().isoformat()
        }
        response.data = custom_data

    return response
