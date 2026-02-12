from webob.response import Response
from tests.constants import BASE_URL

def test_dynamic_dashboard(app, client):
    @app.route("/dashboard")
    def test_handler(req):
        try:
            html_content = app.template(
                template_name="dashboard.html", 
                context={"name": "test_user", "title": "test_title"}
            )
            return Response(
                text=html_content, 
                content_type='text/html'
            )
        except Exception as e:
            # This will help debug
            print(f"Error in handler: {e}")
            raise
    
    response = client.get(f"{BASE_URL}/dashboard")
    
    # Print error details if failed
    if response.status_code != 200:
        print(f"Error response: {response.text}")
        print(f"Status: {response.status_code}")
    
    assert response.status_code == 200
    assert "text/html" in response.headers["Content-Type"]
    assert "test_user" in response.text
    assert "test_title" in response.text