from webob import Request
from roob.common_handlers import CommonHandlers
from roob.framework import Roob


class ErrorHandlerMiddleware:
    def __init__(
            self, 
            app: Roob, 
            exception_handler: callable = CommonHandlers.generic_exception_handler
        ):
        
        self.wrapped_app = app
        self.exception_handler = exception_handler

    def __call__(self, environ, start_response):
        try:
            return self.wrapped_app(environ, start_response)
        except Exception as e:
            request = Request(environ)
            response = self.exception_handler(request, e)
            return response(environ, start_response)