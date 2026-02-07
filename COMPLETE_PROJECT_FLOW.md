# Roob Web Framework - Complete Architecture & Flow

## Table of Contents
1. [Project Overview](#project-overview)
2. [Entry Point & Initialization](#entry-point--initialization)
3. [Request Flow (Step-by-Step)](#request-flow-step-by-step)
4. [Code Architecture](#code-architecture)
5. [Route Registration Process](#route-registration-process)
6. [Request Handling Process](#request-handling-process)
7. [Response Generation](#response-generation)
8. [Error Handling](#error-handling)
9. [Complete Example Trace](#complete-example-trace)
10. [Project Structure](#project-structure)

---

## Project Overview

This is a custom Python web framework called **Roob** that implements:
- ✅ WSGI-compliant web server
- ✅ URL routing with path parameters
- ✅ Class-based views
- ✅ Function-based views
- ✅ HTTP method routing (GET, POST, DELETE, etc.)
- ✅ Middleware support
- ✅ Error handling

---

## Entry Point & Initialization

<<<<<<< HEAD
### 🎯 The Entry Point: `core.main:app`

When you run:
```bash
gunicorn core.main:app
=======
### 🎯 The Entry Point: `core.main:exception_handler_middleware`

When you run:
```bash
gunicorn core.main:exception_handler_middleware
>>>>>>> v1.0_phase-4
```

Gunicorn looks for the `exception_handler_middleware` object in `core/main.py`

### Step 1: Gunicorn Loads `core/main.py`

**File: `core/main.py`**
```python
from core import exception_handler_middleware as app
import core.product_controller as product_controller
```

**What happens:**
1. Line 1: Imports `exception_handler_middleware` from `core/__init__.py`
2. Line 2: Imports `product_controller` module (triggers route registration!)

### Step 2: `core/__init__.py` Executes

**File: `core/__init__.py`**
```python
from roob.framework import Roob
from roob.middlewares import ErrorHandlerMiddleware
from roob.common_handlers import CommonHandlers

# Create the framework instance
app = Roob()

# Wrap it with error handling middleware
exception_handler_middleware = ErrorHandlerMiddleware(
    app=app
)
```

**What happens:**
1. Creates a new `Roob()` instance (the framework)
2. Wraps it with `ErrorHandlerMiddleware` for error handling
3. Exports `exception_handler_middleware` as the WSGI application

### Step 3: Framework Initialization

**File: `roob/framework.py`**
```python
class Roob:
    def __init__(self):
        self.routing_manager = RouteManager()  # Creates empty routes dict

    def __call__(self, environ, start_response):
        # WSGI entry point - called for each HTTP request
        http_request = Request(environ)
        response: Response = self.routing_manager.dispatch(http_request)
        return response(environ, start_response)

    def route(self, path: str):
        # Decorator for registering routes
        def decorator(handler):
            self.routing_manager.register(path, handler)
            return handler
        return decorator
```

**What happens:**
1. Creates a `RouteManager` with an empty `routes = {}` dictionary
2. Provides a `route()` decorator for registering routes
3. Implements `__call__()` to make it a WSGI application

### Step 4: Route Registration (Import Side-Effect)

**File: `core/product_controller.py`**
```python
from core import app  # Gets the Roob instance
from core.data import inventory
from webob import Request, Response
from roob.constants import HttpStatus
from core.service.product_service import ProductService


@app.route('/api/products')  # ← Decorator executes NOW!
class ProductCreatController:
    def __init__(self):
        self.service = ProductService()

    def get(self, request: Request) -> Response:
        return Response(json_body=self.service.get_all_products())

    def post(self, request: Request) -> Response:
        products = self.service.create_new_product(request.json)
        return Response(json_body=products)


@app.route('/api/products/{id:d}')  # ← Decorator executes NOW!
class ProductModifyController:
    def __init__(self):
        self.service = ProductService()

    def get(self, request: Request, id: int) -> Response:
        product = self.service.get_product_by_id(id)
        if not product:
            return Response(
                json_body={"message": f"No product found with product id {id}"},
                status=HttpStatus.NOT_FOUND
            )
        return Response(json_body=product)

    def delete(self, request: Request, id: int):
        try:
            products = self.service.delete_product_by_id(id)
            return Response(json_body=products)
        except Exception as e:
            return Response(
                json_body={"message": str(e)},
                status=HttpStatus.NOT_FOUND
            )


@app.route('/api/products/{category}')  # ← Decorator executes NOW!
def get_products_by_cat(request: Request, category: str) -> Response:
    if category not in inventory:
        return Response(
            json_body={"message": f"{category} doesn't exist in the inventory"},
            status=HttpStatus.NOT_FOUND,
        )
    return Response(json_body=inventory[category])
```

**What happens when this module is imported:**
1. The `@app.route()` decorators execute immediately
2. Each decorator calls `app.routing_manager.register(path, handler)`
3. Routes are stored in the `routes` dictionary:

```python
routes = {
    '/api/products': ProductCreatController,  # Class
    '/api/products/{id:d}': ProductModifyController,  # Class
    '/api/products/{category}': get_products_by_cat  # Function
}
```

**At this point, initialization is complete! The server is ready to handle requests.**

---

## Request Flow (Step-by-Step)

Let's trace a complete request: `GET http://localhost:8000/api/products`

### Step 1: HTTP Request Arrives at Gunicorn

```
Client → HTTP GET /api/products → Gunicorn Worker Process
```

Gunicorn receives the raw HTTP request and creates a WSGI `environ` dictionary containing all request data.

### Step 2: Gunicorn Calls the WSGI Application

```python
# Gunicorn internally does something like:
response = exception_handler_middleware(environ, start_response)
```

### Step 3: Middleware Processes Request

**File: `roob/middlewares.py`**
```python
class ErrorHandlerMiddleware:
    def __init__(self, app):
        self.app = app  # The Roob framework

    def __call__(self, environ, start_response):
        try:
            # Call the wrapped application
            return self.app(environ, start_response)
        except Exception as e:
            # If any exception occurs, handle it gracefully
            request = Request(environ)
            response = CommonHandlers.generic_exception_handler(request, e)
            return response(environ, start_response)
```

**What happens:**
1. Wraps the framework call in try-except
2. If no error: passes request to `self.app` (Roob framework)
3. If error: catches it and returns error response

### Step 4: Framework Receives Request

**File: `roob/framework.py`**
```python
class Roob:
    def __call__(self, environ, start_response):
        # Convert WSGI environ to WebOb Request
        http_request = Request(environ)
        
        # Dispatch to the appropriate handler
        response: Response = self.routing_manager.dispatch(http_request)
        
        # Return WSGI response
        return response(environ, start_response)
```

**What happens:**
1. Converts WSGI `environ` dict to a `Request` object (easier to work with)
2. Calls `routing_manager.dispatch()` to find and execute the handler
3. Converts the `Response` object back to WSGI format

### Step 5: Route Manager Dispatches Request

**File: `roob/routing_manager.py`**
```python
class RouteManager:
    def __init__(self):
        self.routes = {}

    def register(self, path, handler):
        if path in self.routes:
            raise RuntimeError(f"Path: {path} already bind to another handler")
        self.routes[path] = handler

    def dispatch(self, http_request: Request):
        # Find the matching handler
        handler, kwargs = RoutingHelper.get_handler(self.routes, http_request)
        
        # Execute the handler with extracted parameters
        return handler(http_request, **kwargs)
```

**What happens:**
1. Calls `RoutingHelper.get_handler()` to find the matching route
2. Executes the handler with the request and any URL parameters
3. Returns the response

### Step 6: Routing Helper Finds Handler

**File: `roob/helpers.py`**
```python
class RoutingHelper:
    @classmethod
    def _find_handler(cls, routes: dict, request: Request) -> tuple:
        # Normalize URL (remove trailing slash if present)
        requested_path = normalize_request_url(request.path)
        # requested_path = "/api/products"

        # Check for exact match
        if requested_path in routes:
            return routes[requested_path], {}
            # Returns: (ProductCreatController, {})

        # Check for pattern match (with path parameters)
        for path, handler in routes.items():
            parsed = parse(path, requested_path)
            if parsed:
                return handler, parsed.named
                # Would return: (ProductModifyController, {'id': 1})
                # for request: /api/products/1

        # No match found - return 404 handler
        return CommonHandlers.url_not_found_handler, {}
    
    @classmethod
    def _find_class_based_handler(cls, handler_class, request: Request, kwargs: dict) -> tuple:
        # Instantiate the class
        handler_instance = handler_class()
        # handler_instance = ProductCreatController()
        
        # Get HTTP method in lowercase
        method_name = request.method.lower()
        # method_name = "get"
        
        # Check if the handler has this method
        if hasattr(handler_instance, method_name):
            handler_method = getattr(handler_instance, method_name)
            # handler_method = ProductCreatController.get
            return handler_method, kwargs
        
        # Method not allowed
        return CommonHandlers.method_not_allowed_handler, {}
    
    @classmethod
    def get_handler(cls, routes: dict, request: Request) -> tuple:
        # Find the handler (class or function)
        handler, kwargs = cls._find_handler(routes, request)
        # handler = ProductCreatController
        # kwargs = {}
        
        # If it's a class, instantiate it and find the HTTP method
        if inspect.isclass(handler):
            handler, kwargs = cls._find_class_based_handler(handler, request, kwargs)
            # handler = ProductCreatController().get
            # kwargs = {}
        
        return handler, kwargs
```

**What happens for `GET /api/products`:**
1. `_find_handler()` finds exact match: `ProductCreatController`
2. Detects it's a class (not a function)
3. `_find_class_based_handler()`:
   - Instantiates: `ProductCreatController()`
   - Request method is GET → finds `.get()` method
   - Returns: `(ProductCreatController().get, {})`

### Step 7: Controller Executes

**File: `core/product_controller.py`**
```python
class ProductCreatController:
    def __init__(self):
        self.service = ProductService()

    def get(self, request: Request) -> Response:
        # Get all products from service
        return Response(
            json_body=self.service.get_all_products()
        )
```

**What happens:**
1. `ProductCreatController()` is instantiated
2. `get()` method is called with the request
3. Calls `self.service.get_all_products()`

### Step 8: Service Layer Executes

**File: `core/service/product_service.py`**
```python
class ProductService:
    def get_all_products(self) -> list[dict]:
        return inventory
```

**File: `core/data.py`**
```python
inventory = {
    "mobile": [
        {"product_id": 1, "product_name": "S25 Ultra", "brand": "Samsung"},
        {"product_id": 2, "product_name": "iPhone", "brand": "Apple"}
    ],
    "laptop": [
        {"product_id": 3, "product_name": "Macbook Pro M4", "brand": "Apple"},
        {"product_id": 4, "product_name": "Dell XPS", "brand": "Dell"}
    ]
}
```

**What happens:**
1. Returns the `inventory` dictionary

### Step 9: Response Created

```python
Response(json_body=inventory)
```

**What happens:**
1. WebOb creates a Response object
2. Serializes the Python dict to JSON
3. Sets appropriate headers (`Content-Type: application/json`)
4. Sets status code (200 OK by default)

### Step 10: Response Travels Back

```
Controller → RouteManager → Roob Framework → Middleware → Gunicorn → Client
```

**Response object contains:**
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 234

{
  "mobile": [
    {"product_id": 1, "product_name": "S25 Ultra", "brand": "Samsung"},
    {"product_id": 2, "product_name": "iPhone", "brand": "Apple"}
  ],
  "laptop": [
    {"product_id": 3, "product_name": "Macbook Pro M4", "brand": "Apple"},
    {"product_id": 4, "product_name": "Dell XPS", "brand": "Dell"}
  ]
}
```

---

## Code Architecture

### Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Client                              │
│                   (Browser, curl, etc.)                     │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP Request
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      Gunicorn (WSGI Server)                 │
│                  - Manages worker processes                 │
│                  - Handles concurrency                      │
└────────────────────────────┬────────────────────────────────┘
                             │ WSGI environ dict
                             ▼
┌─────────────────────────────────────────────────────────────┐
│             Middleware Layer (roob/middlewares.py)          │
│                  - Error handling                           │
│                  - Exception catching                       │
│                  - Logging (if needed)                      │
└────────────────────────────┬────────────────────────────────┘
                             │ WebOb Request
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              Framework Layer (roob/framework.py)            │
│                     - Roob class                            │
│                     - Route decorator                       │
│                     - WSGI interface                        │
└────────────────────────────┬────────────────────────────────┘
                             │ Dispatch request
                             ▼
┌─────────────────────────────────────────────────────────────┐
│           Routing Layer (roob/routing_manager.py)           │
│                  - RouteManager                             │
│                  - Stores registered routes                 │
│                  - Dispatches to handlers                   │
└────────────────────────────┬────────────────────────────────┘
                             │ Find handler
                             ▼
┌─────────────────────────────────────────────────────────────┐
│             Helper Layer (roob/helpers.py)                  │
│                  - RoutingHelper                            │
│                  - URL pattern matching                     │
│                  - Class-based view handling                │
│                  - HTTP method routing                      │
└────────────────────────────┬────────────────────────────────┘
                             │ Execute handler
                             ▼
┌─────────────────────────────────────────────────────────────┐
│          Controller Layer (core/product_controller.py)      │
│                  - ProductCreatController                   │
│                  - ProductModifyController                  │
│                  - get_products_by_cat                      │
└────────────────────────────┬────────────────────────────────┘
                             │ Business logic
                             ▼
┌─────────────────────────────────────────────────────────────┐
│       Service Layer (core/service/product_service.py)       │
│                  - ProductService                           │
│                  - Business logic                           │
│                  - Data manipulation                        │
└────────────────────────────┬────────────────────────────────┘
                             │ Data access
                             ▼
┌─────────────────────────────────────────────────────────────┐
│               Data Layer (core/data.py)                     │
│                  - inventory dict                           │
│                  - products list                            │
│                  (In real app: Database access)             │
└─────────────────────────────────────────────────────────────┘
```

---

## Route Registration Process

### Visual Flow

```
Application Startup
       │
       ▼
Load core/main.py
       │
       ├──→ Import core/__init__.py
       │         │
       │         ├──→ Create Roob() instance
       │         │         │
       │         │         └──→ Create RouteManager()
       │         │                    │
       │         │                    └──→ routes = {}
       │         │
       │         └──→ Wrap with ErrorHandlerMiddleware
       │
       ▼
Import core/product_controller.py
       │
       ├──→ @app.route('/api/products')
       │         │
       │         └──→ app.route('/api/products')(ProductCreatController)
       │                    │
       │                    └──→ routing_manager.register('/api/products', ProductCreatController)
       │                              │
       │                              └──→ routes['/api/products'] = ProductCreatController
       │
       ├──→ @app.route('/api/products/{id:d}')
       │         │
       │         └──→ routes['/api/products/{id:d}'] = ProductModifyController
       │
       └──→ @app.route('/api/products/{category}')
                 │
                 └──→ routes['/api/products/{category}'] = get_products_by_cat
       
Routes registered! Server ready to handle requests.
```

---

## Request Handling Process

### Example 1: `GET /api/products`

```
HTTP GET /api/products
       │
       ▼
Gunicorn Worker
       │
       ▼
exception_handler_middleware(environ, start_response)
       │
       ├──→ try:
       │      app(environ, start_response)
       │
       ▼
Roob.__call__(environ, start_response)
       │
       ├──→ http_request = Request(environ)
       │         │
       │         └──→ Creates WebOb Request object
       │                  - method = "GET"
       │                  - path = "/api/products"
       │                  - headers = {...}
       │                  - body = ""
       │
       ├──→ response = routing_manager.dispatch(http_request)
       │
       ▼
RouteManager.dispatch(http_request)
       │
       ├──→ handler, kwargs = RoutingHelper.get_handler(routes, http_request)
       │
       ▼
RoutingHelper.get_handler(routes, http_request)
       │
       ├──→ handler, kwargs = _find_handler(routes, http_request)
       │         │
       │         ├──→ requested_path = "/api/products"
       │         ├──→ Check exact match: "/api/products" in routes? YES!
       │         └──→ return (ProductCreatController, {})
       │
       ├──→ Is handler a class? YES!
       │
       ├──→ handler, kwargs = _find_class_based_handler(handler, request, kwargs)
       │         │
       │         ├──→ handler_instance = ProductCreatController()
       │         │         │
       │         │         └──→ self.service = ProductService()
       │         │
       │         ├──→ method_name = request.method.lower() = "get"
       │         ├──→ handler_method = getattr(handler_instance, "get")
       │         └──→ return (ProductCreatController().get, {})
       │
       └──→ return (ProductCreatController().get, {})
       
       ▼
RouteManager.dispatch() continues:
       │
       └──→ return handler(http_request, **kwargs)
              │
              └──→ return ProductCreatController().get(http_request)
       
       ▼
ProductCreatController.get(request)
       │
       ├──→ return Response(json_body=self.service.get_all_products())
       │
       ▼
ProductService.get_all_products()
       │
       └──→ return inventory
              │
              └──→ Returns the inventory dict
       
       ▼
Response object created:
       │
       ├──→ status = 200 OK
       ├──→ headers = {"Content-Type": "application/json"}
       └──→ body = JSON serialized inventory
       
       ▼
Response travels back through the stack:
       │
       ├──→ RouteManager.dispatch() returns response
       ├──→ Roob.__call__() returns response(environ, start_response)
       ├──→ Middleware catches no exception, passes through
       └──→ Gunicorn sends HTTP response to client
```

### Example 2: `GET /api/products/1`

```
HTTP GET /api/products/1
       │
       ▼
... (same as above until routing) ...
       │
       ▼
RoutingHelper._find_handler(routes, request)
       │
       ├──→ requested_path = "/api/products/1"
       ├──→ Check exact match: "/api/products/1" in routes? NO
       │
       ├──→ Loop through routes with patterns:
       │      for path, handler in routes.items():
       │
       ├──→ Try: parse('/api/products', '/api/products/1')
       │         Result: None (doesn't match)
       │
       ├──→ Try: parse('/api/products/{id:d}', '/api/products/1')
       │         Result: parsed.named = {'id': 1}  ✓ MATCH!
       │
       └──→ return (ProductModifyController, {'id': 1})
       
       ▼
RoutingHelper._find_class_based_handler(ProductModifyController, request, {'id': 1})
       │
       ├──→ handler_instance = ProductModifyController()
       ├──→ method_name = "get"
       ├──→ handler_method = ProductModifyController().get
       └──→ return (ProductModifyController().get, {'id': 1})
       
       ▼
RouteManager.dispatch():
       │
       └──→ return handler(http_request, **kwargs)
              │
              └──→ return ProductModifyController().get(http_request, id=1)
       
       ▼
ProductModifyController.get(request, id=1)
       │
       ├──→ product = self.service.get_product_by_id(1)
       │         │
       │         └──→ ProductService.get_product_by_id(1)
       │                  │
       │                  ├──→ Loop through products
       │                  ├──→ Find product with id == 1
       │                  └──→ return {"id": 1, "product_name": "S25 Ultra", "brand": "Samsung"}
       │
       ├──→ if not product: (False, product found)
       │
       └──→ return Response(json_body=product)
       
       ▼
Response sent back to client
```

### Example 3: `POST /api/products`

```
HTTP POST /api/products
Content-Type: application/json
Body: {"id": 5, "product_name": "Galaxy Tab", "brand": "Samsung"}
       │
       ▼
... (same routing as GET /api/products) ...
       │
       ▼
RoutingHelper._find_class_based_handler(ProductCreatController, request, {})
       │
       ├──→ handler_instance = ProductCreatController()
       ├──→ method_name = "post"  ← Different method!
       ├──→ handler_method = ProductCreatController().post
       └──→ return (ProductCreatController().post, {})
       
       ▼
ProductCreatController.post(request)
       │
       ├──→ products = self.service.create_new_product(request.json)
       │         │
       │         │ request.json = {"id": 5, "product_name": "Galaxy Tab", "brand": "Samsung"}
       │         │
       │         └──→ ProductService.create_new_product(product)
       │                  │
       │                  ├──→ products.append(product)
       │                  └──→ return products
       │
       └──→ return Response(json_body=products)
       
       ▼
Response sent with updated products list
```

### Example 4: `DELETE /api/products/2`

```
HTTP DELETE /api/products/2
       │
       ▼
... (routes to ProductModifyController) ...
       │
       ▼
RoutingHelper._find_class_based_handler(ProductModifyController, request, {'id': 2})
       │
       ├──→ handler_instance = ProductModifyController()
       ├──→ method_name = "delete"  ← DELETE method!
       ├──→ handler_method = ProductModifyController().delete
       └──→ return (ProductModifyController().delete, {'id': 2})
       
       ▼
ProductModifyController.delete(request, id=2)
       │
       ├──→ try:
       │      products = self.service.delete_product_by_id(2)
       │            │
       │            └──→ ProductService.delete_product_by_id(2)
       │                     │
       │                     ├──→ product = self.get_product_by_id(2)
       │                     ├──→ if not product: raise Exception(...)
       │                     ├──→ products.remove(product)
       │                     └──→ return products
       │
       └──→ return Response(json_body=products)
       
       ▼
Response sent with remaining products
```

---

## Response Generation

### How Responses Are Created

**File: `webob` library (external)**
```python
Response(
    json_body=data,           # Python dict/list → JSON
    status=200,               # HTTP status code
    headers={'Custom': 'Value'}  # Optional headers
)
```

**What WebOb does:**
1. Serializes `json_body` to JSON string
2. Sets `Content-Type: application/json` header
3. Sets `Content-Length` header
4. Creates WSGI-compliant response

**Response object structure:**
```python
response = Response(json_body={"message": "Success"})

# Internal structure:
response.status = "200 OK"
response.headers = {
    'Content-Type': 'application/json',
    'Content-Length': '23'
}
response.body = b'{"message": "Success"}'
```

---

## Error Handling

### Case 1: Route Not Found

```
HTTP GET /api/invalid
       │
       ▼
RoutingHelper._find_handler(routes, request)
       │
       ├──→ requested_path = "/api/invalid"
       ├──→ Check exact match: NO
       ├──→ Check pattern matches: NO
       │
       └──→ return (CommonHandlers.url_not_found_handler, {})
       
       ▼
CommonHandlers.url_not_found_handler(request)
       │
       └──→ return Response(
              json_body={"message": "Requested path: /api/invalid does not exist"},
              status=404
            )
```

### Case 2: Method Not Allowed

```
HTTP PUT /api/products  ← PUT not supported!
       │
       ▼
RoutingHelper._find_class_based_handler(ProductCreatController, request, {})
       │
       ├──→ handler_instance = ProductCreatController()
       ├──→ method_name = "put"
       ├──→ hasattr(handler_instance, "put")? NO!
       │
       └──→ return (CommonHandlers.method_not_allowed_handler, {})
       
       ▼
CommonHandlers.method_not_allowed_handler(request)
       │
       └──→ return Response(
              json_body={"message": "PUT request is not allowed for /api/products"},
              status=405
            )
```

### Case 3: Unhandled Exception

```
HTTP GET /api/products
       │
       ▼
ProductCreatController.get(request)
       │
       └──→ self.service.get_all_products()
              │
              └──→ CRASH! (Simulated error)
       
       ▼
Exception bubbles up to middleware:
       │
       ▼
ErrorHandlerMiddleware.__call__(environ, start_response)
       │
       ├──→ try:
       │      app(environ, start_response)  ← Exception raised here!
       │
       ├──→ except Exception as e:
       │      request = Request(environ)
       │      response = CommonHandlers.generic_exception_handler(request, e)
       │
       ▼
CommonHandlers.generic_exception_handler(request, exception)
       │
       ├──→ logger.exception(exception)  ← Log the error
       │
       └──→ return Response(
              json_body={"message": "Unhanded Exception Occurred: ..."},
              status=500
            )
       
       ▼
Error response sent to client, server continues running!
```

---

## Complete Example Trace

Let's trace **`curl -X POST http://localhost:8000/api/products -d '{"id":5,"product_name":"Test","brand":"TestCo"}'`**

### Timeline

```
T=0ms: Client sends HTTP POST request
       │
T=1ms: Gunicorn worker receives request
       │
       ├──→ Creates WSGI environ dict:
       │      {
       │        'REQUEST_METHOD': 'POST',
       │        'PATH_INFO': '/api/products',
       │        'CONTENT_TYPE': 'application/json',
       │        'wsgi.input': <file-like object with body>,
       │        ... (50+ more fields)
       │      }
       │
       └──→ Calls: exception_handler_middleware(environ, start_response)
       
T=2ms: ErrorHandlerMiddleware.__call__() executes
       │
       └──→ try: self.app(environ, start_response)
       
T=3ms: Roob.__call__() executes
       │
       ├──→ http_request = Request(environ)
       │      {
       │        method: 'POST',
       │        path: '/api/products',
       │        json: {'id': 5, 'product_name': 'Test', 'brand': 'TestCo'}
       │      }
       │
       └──→ response = self.routing_manager.dispatch(http_request)
       
T=4ms: RouteManager.dispatch() executes
       │
       └──→ handler, kwargs = RoutingHelper.get_handler(self.routes, http_request)
       
T=5ms: RoutingHelper.get_handler() executes
       │
       ├──→ handler, kwargs = _find_handler(routes, request)
       │      Loop through routes:
       │      - '/api/products' == '/api/products'? YES!
       │      - return (ProductCreatController, {})
       │
       ├──→ inspect.isclass(ProductCreatController)? YES!
       │
       └──→ handler, kwargs = _find_class_based_handler(ProductCreatController, request, {})
              │
              ├──→ handler_instance = ProductCreatController()
              │      │
              │      └──→ self.service = ProductService()
              │
              ├──→ method_name = 'post'
              ├──→ handler_method = getattr(handler_instance, 'post')
              └──→ return (ProductCreatController().post, {})
       
T=6ms: RouteManager.dispatch() continues
       │
       └──→ return handler(http_request, **kwargs)
              │
              └──→ return ProductCreatController().post(http_request)
       
T=7ms: ProductCreatController.post() executes
       │
       ├──→ products = self.service.create_new_product(request.json)
       │
       ▼
       
T=8ms: ProductService.create_new_product() executes
       │
       ├──→ products.append({'id': 5, 'product_name': 'Test', 'brand': 'TestCo'})
       │      
       │      products = [
       │        {'id': 1, 'product_name': 'S25 Ultra', 'brand': 'Samsung'},
       │        {'id': 2, 'product_name': 'iPhone', 'brand': 'Apple'},
       │        {'id': 5, 'product_name': 'Test', 'brand': 'TestCo'}  ← NEW!
       │      ]
       │
       └──→ return products
       
T=9ms: ProductCreatController.post() continues
       │
       └──→ return Response(json_body=products)
              │
              └──→ Creates WebOb Response:
                     status: 200 OK
                     headers: {'Content-Type': 'application/json'}
                     body: '[{"id":1,...},{"id":2,...},{"id":5,...}]'
       
T=10ms: Response bubbles back up:
       │
       ├──→ RouteManager.dispatch() returns response
       ├──→ Roob.__call__() returns response(environ, start_response)
       ├──→ ErrorHandlerMiddleware catches no exception
       └──→ Gunicorn receives WSGI response tuple
       
T=11ms: Gunicorn sends HTTP response:
       │
       └──→ HTTP/1.1 200 OK
            Content-Type: application/json
            Content-Length: 156
            
            [
              {"id": 1, "product_name": "S25 Ultra", "brand": "Samsung"},
              {"id": 2, "product_name": "iPhone", "brand": "Apple"},
              {"id": 5, "product_name": "Test", "brand": "TestCo"}
            ]
       
T=12ms: Client receives response ✓
```

---

## Project Structure

```
WebFramework_scratch-main-FIXED/
│
├── core/                           # Application code
│   ├── __init__.py                 # Creates app & middleware (entry point setup)
│   ├── main.py                     # WSGI entry point (imports for initialization)
│   ├── wsgi_server.py              # Development WSGI server runner
│   ├── data.py                     # Sample data (inventory, products)
│   │
│   ├── product_controller.py       # Route handlers
│   │   ├── ProductCreatController  # GET/POST /api/products
│   │   ├── ProductModifyController # GET/DELETE /api/products/{id}
│   │   └── get_products_by_cat()   # GET /api/products/{category}
│   │
│   └── service/                    # Business logic layer
│       ├── __init__.py
│       └── product_service.py      # ProductService class
│
├── roob/                           # Framework code
│   ├── __init__.py
│   │
│   ├── framework.py                # Main framework (Roob class)
│   │   ├── __init__()              # Creates RouteManager
│   │   ├── __call__()              # WSGI entry point
│   │   └── route()                 # Decorator for registering routes
│   │
│   ├── routing_manager.py          # Route registration & dispatch
│   │   ├── register()              # Add route to routes dict
│   │   └── dispatch()              # Find and execute handler
│   │
│   ├── helpers.py                  # Routing logic
│   │   ├── _find_handler()         # Match URL to handler
│   │   ├── _find_class_based_handler()  # Handle class views
│   │   └── get_handler()           # Main routing function
│   │
│   ├── middlewares.py              # Middleware implementations
│   │   └── ErrorHandlerMiddleware  # Catches exceptions
│   │
│   ├── common_handlers.py          # Error response handlers
│   │   ├── url_not_found_handler()     # 404 responses
│   │   ├── method_not_allowed_handler() # 405 responses
│   │   └── generic_exception_handler()  # 500 responses
│   │
│   └── constants.py                # HTTP status constants
│
├── run_server.py                   # Launcher script (dev server)
├── run_gunicorn.sh                 # Shell script for Gunicorn
├── gunicorn_config.py              # Gunicorn configuration
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## Key Concepts Summary

### 1. **WSGI (Web Server Gateway Interface)**
- Standard interface between web servers and Python applications
- Application is a callable that takes `(environ, start_response)`
- Returns an iterable of byte strings (the HTTP response)

### 2. **Decorators for Route Registration**
```python
@app.route('/api/products')
class ProductCreatController:
    ...
```
- Decorator executes when the module is imported
- Registers the route in the RouteManager's routes dictionary
- Import side-effect is intentional and necessary

### 3. **Class-Based Views**
- Controllers are classes with HTTP method names as methods
- `get()`, `post()`, `delete()`, `put()`, `patch()`
- Framework instantiates the class and calls the appropriate method
- Allows code organization and state sharing via `self`

### 4. **URL Pattern Matching**
- Uses the `parse` library for pattern matching
- `{id:d}` matches integers and extracts them
- `{category}` matches any string
- Extracted parameters passed as keyword arguments to handlers

### 5. **Middleware Pattern**
- Wraps the application to add functionality
- ErrorHandlerMiddleware catches exceptions
- Can add logging, authentication, CORS, etc.

### 6. **Service Layer Pattern**
- Controllers are thin, delegate to services
- Services contain business logic
- Separates concerns: routing vs. logic vs. data

### 7. **Response Objects**
- WebOb Response objects for easy HTTP response creation
- `json_body` parameter auto-serializes to JSON
- Sets appropriate headers automatically

---

## Running the Project

### Development
```bash
# Using Python
python run_server.py

# Using Gunicorn with auto-reload
./run_gunicorn.sh development
```

### Production
```bash
# Using Gunicorn with multiple workers
./run_gunicorn.sh production

# Or with config file
gunicorn -c gunicorn_config.py core.main:exception_handler_middleware
```

---

## Testing the API

```bash
# Get all products
curl http://localhost:8000/api/products

# Create a product
curl -X POST http://localhost:8000/api/products \
  -H "Content-Type: application/json" \
  -d '{"id": 5, "product_name": "Galaxy Tab", "brand": "Samsung"}'

# Get product by ID
curl http://localhost:8000/api/products/1

# Delete product
curl -X DELETE http://localhost:8000/api/products/2

# Get products by category
curl http://localhost:8000/api/products/mobile
```

---

## Dependencies

- **webob** - HTTP request/response objects
- **parse** - URL pattern parsing
- **gunicorn** - Production WSGI server

Install with:
```bash
pip install -r requirements.txt
```

---

## Conclusion

This framework demonstrates core web framework concepts:

1. ✅ **WSGI compliance** - Works with any WSGI server
2. ✅ **Routing** - URL pattern matching with parameters
3. ✅ **Class-based views** - HTTP method routing
4. ✅ **Middleware** - Request/response processing
5. ✅ **Error handling** - Graceful exception handling
6. ✅ **Separation of concerns** - Controllers → Services → Data

The flow is:
```
Client → Gunicorn → Middleware → Framework → Router → Controller → Service → Data
```

And back:
```
Data → Service → Controller → Router → Framework → Middleware → Gunicorn → Client
```

Every HTTP request goes through this complete cycle, ensuring proper routing, error handling, and response generation!
