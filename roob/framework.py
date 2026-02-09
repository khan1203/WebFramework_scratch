from roob.routing_manager import RouteManager
from webob import Request, Response
from jinja2 import Environment, FileSystemLoader
import os


class Roob:
    def __init__(self, template_dir: str = "templates"):
        self.routing_manager = RouteManager()

        # Initialize jinja2 env
        self.templates_env = Environment(
            loader = FileSystemLoader(os.path.abspath(template_dir))
        )

    def __call__(self, environ, start_response):
        http_request = Request(environ)
        response: Response = self.routing_manager.dispatch(http_request)
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

