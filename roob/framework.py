from whitenoise import WhiteNoise
from roob.routing_manager import RouteManager
from webob import Request, Response
from jinja2 import Environment, FileSystemLoader

import os
from typing import Optional

class Roob:
    def __init__(self, template_dir: str = "templates", static_dir: str = "static"):
        self.routing_manager = RouteManager()

        # Initialize jinja2 env
        self.templates_env = Environment(
            loader = FileSystemLoader(os.path.abspath(template_dir))
        )

        #Initialize whitenoise proxy
        self.whitenoise = WhiteNoise(
            application=self.wsgi_app,
            root=static_dir
        )

        self.exception_handler: Optional[callable] = None

    #Evoluton = 1.0 -----------------------------------
    '''
    def __call__(self, environ, start_response):
        http_request = Request(environ)
        response: Response = self.routing_manager.dispatch(http_request)
        return response(environ, start_response)
    '''
    #Evoluton = 2.0 -----------------------------------
    '''
    def __call__(self, environ, start_response):
        http_request = Request(environ)
        try:
            response: Response = self.routing_manager.dispatch(http_request)
        except Exception as e:
            if not self.exception_handler:
                raise e
            response: Response = self.exception_handler(http_request, e)
        return response(environ, start_response)
    '''
    #Evolution = 3.0 -----------------------------------
    def __call__(self, environ, start_response):
        return self.whitenoise(environ, start_response)

    def wsgi_app(self, environ, start_response):
        http_request = Request(environ)
        response = self._handle_request(http_request)
        return response(environ, start_response)

    def route(self, path: str):
        def decorator(handler):
            self.routing_manager.register(path, handler)
            return handler
        return decorator
    
    def add_route(self, path:str, handler:callable)-> None:
        """
        Django style explicit route registration.
        :param path:
        :param handler:
        :return:
        """
        self.routing_manager.register(path, handler)

    def template(self, template_name:str, context: dict)->str:
        if context is None:
            context = {}
        
        return self.templates_env.get_template(template_name).render(**context)

    def add_exception_handler(self, handler: callable) -> None:
        self.exception_handler = handler
    
    def _handle_request(self, request: Request) -> Response:
        # Handle Requests that are not made for any static file
        try:
            return self.routing_manager.dispatch(request)
        except Exception as e:
            if not self.exception_handler:
                raise e
            return self.exception_handler(request, e)

