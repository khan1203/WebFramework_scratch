from common_handlers import CommonHandlers
from middlewares import ErrorHandlerMiddleware
from routing_manager import RouteManager
from webob import Request, Response


class Application:
    def __init__(self):
        self.routing_manager = RouteManager()

    def __call__(self, environ, start_response):
        http_request = Request(environ)
        response: Response = self.routing_manager.dispatch(http_request)
        return response(environ, start_response)

    def route(self, path):
        def decorator(handler):
            self.routing_manager.register(path, handler)
            return handler
        return decorator


app = Application()
middleware = ErrorHandlerMiddleware(
    app=app,
    exception_handler=CommonHandlers.generic_exception_handler
)