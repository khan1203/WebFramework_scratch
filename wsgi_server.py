from wsgiref.simple_server import make_server
from app import middleware
import product_controller

if __name__ == "__main__":
    host = "localhost"
    port = 8000
    with make_server(host, port, app=middleware) as server:
        print(f"Listening to http://{host}:{port}")
        server.serve_forever()