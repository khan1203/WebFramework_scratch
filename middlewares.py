from webob import Request


class ErrorHandlerMiddleware:
    def __init__(self, app, exception_handler: callable):
        self.wrapped_app = app
        self.exception_handler = exception_handler

    def __call__(self, environ, start_response):
        try:
            return self.wrapped_app(environ, start_response)
        except Exception as e:
            request = Request(environ)
            response = self.exception_handler(request, e)
            return response(environ, start_response)