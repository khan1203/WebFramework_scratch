import pytest
from webob.response import Response

from tests.constants import BASE_URL


def test_client_can_send_requests(app, client):
    RESPONSE_TEXT = "Hello from test client (Request)"

    @app.route("/test")
    def test_handler(req):
        return Response(text=RESPONSE_TEXT)

    response = client.get(f"{BASE_URL}/test")
    assert response.text == RESPONSE_TEXT


@pytest.mark.parametrize(
    "name, exp_result",
    [
        pytest.param(
            "Alice", "Hello Alice", id="Alice",
        ),
        pytest.param(
            "Bob", "Hello Bob", id="Bob",
        ),
        pytest.param(
            "Charlie", "Hello Charlie", id="Charlie",
        )
    ]
)

def test_parameterized_route(app, client, name, exp_result):
    @app.route("/hello/{name}")
    def hello(req, name: str):
        return Response(text=f"Hello {name}")
    assert client.get(f"{BASE_URL}/hello/{name}").text == exp_result


def test_url_not_found(app, client):
    RESPONSE_TEXT = "Hello from test client"
    exp_response = {
        "message": f"Requested path: /hello does not exist"
    }

    @app.route("/test")
    def test_handler(req):
        return Response(text=RESPONSE_TEXT)

    response = client.get(f"{BASE_URL}/hello")
    assert response.status_code == 404
    assert response.json() == exp_response


def test_generic_exception_handler(app, client):
    msg = "A test exception"
    exp_response = {
        "message": f"Unhanded Exception Occurred: {msg}"
    }

    @app.route("/test")
    def test_handler(req):
        raise RuntimeError(msg)

    response = client.get(f"{BASE_URL}/test")
    assert response.status_code == 500
    assert response.json() == exp_response