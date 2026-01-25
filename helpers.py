import json
from http import HTTPStatus


def json_response(
    response: dict | list[dict],
    start_response, status=HTTPStatus.OK,
    response_headers=[]
) -> list[bytes]:
    
    response_body = json.dumps(response)
    response_headers.append(
         ('Content-type', 'text/json')
    )

    # Call start_response with status and headers
    start_response(status, response_headers)

    # Return response body as bytes in an iterable
    return [response_body.encode('utf-8')]


def normalize_request_url(url):
    if url != "/" and url.endswith("/"):
        return url[:-1]
    return url