from rest_framework.views import Response
from typing import Any, Dict
from http import HTTPStatus
from rest_framework.views import exception_handler


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Response:
    """Custom API exception handler."""

    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # Using the description's of the HTTPStatus class as error message.
        http_code_to_message = {v.value: v.description for v in HTTPStatus}

        error_payload = {
            "status_code": response.status_code,
            "error": "",
            "payload": [],
        }

        error_response_key = list(response.data.keys())[0]
        if error_response_key == 'detail':
            error_message = f"{response.data.get(error_response_key)}"
        elif error_response_key == 'error':
            error_message = f"{response.data.get(error_response_key)[0]}"
        else:
            error_message = f"'{error_response_key}': {response.data.get(error_response_key)[0]}"

        error_payload["error"] = error_message
        error_payload["payload"] = response.data
        response.data = error_payload
    return response


...
