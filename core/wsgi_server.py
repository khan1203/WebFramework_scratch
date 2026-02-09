import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from wsgiref.simple_server import make_server
from core import exception_handler_middleware as middleware
import core.api.product_controller as product_controller

if __name__ == "__main__":
    host = "localhost"
    port = 8000
    with make_server(host, port, app=middleware) as server:
        print(f"Listening to http://{host}:{port}")
        server.serve_forever()
