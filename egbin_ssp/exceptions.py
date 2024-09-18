from rest_framework.views import exception_handler
from rest_framework.serializers import ValidationError
from rest_framework.exceptions import APIException


def custom_exception_handler(exc, context):
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    # Initialize an empty list to store all errors
    errors_list = []
    if response is not None:

        if isinstance(response.data, dict):
            for field, error_messages in response.data.items():
                if field == 'non_field_errors':
                    for error in error_messages:
                        errors_list.append(f"{error}")
                else:
                    if isinstance(error_messages, list):
                        for error in error_messages:
                            errors_list.append(f"{error}")
                    else:
                        errors_list.append(f"{error_messages}")

        elif isinstance(response.data, list):
            for error in response.data:
                errors_list.append(str(error))
        else:
            errors_list.append(str(response.data))

        # Format the response with the status_code and standardized error list
        response.data = {
            'status_code': response.status_code,
            'errors': errors_list
        }

    return response




class SerializerValidationException(APIException):
    status_code =400
    default_detail = 'An error occured'
    default_code = 'error'