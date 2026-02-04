import inspect
from webob import Request

from parse import parse
from roob.common_handlers import CommonHandlers


def normalize_request_url(url):
    if url != "/" and url.endswith("/"):
        return url[:-1]
    return url

class RoutingHelper:
    @classmethod
    def _find_handler(cls, routes: dict, request: Request) -> tuple:
        requested_path = normalize_request_url(request.path)

        if requested_path in routes:
            return routes[requested_path], {}

        # url that contains path variable
        for path, handler in routes.items():
            parsed = parse(path, requested_path)
            if parsed:
                return handler, parsed.named

        # default fallback handler
        return CommonHandlers.url_not_found_handler, {}
    
    @classmethod
    def get_handler(cls, routes: dict, request: Request) -> tuple:
        handler, kwargs = cls._find_handler(routes, request)
        if inspect.isclass(handler):
            handler, kwargs = cls._find_class_based_handler(handler, request, kwargs)
        return handler, kwargs