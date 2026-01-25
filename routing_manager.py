from parse import parse
from webob import Request
from common_handlers import CommonHandlers
from helpers import normalize_request_url


class RouteManager:
    def __init__(self):
        self.routes = {}

    def register(self, path, handler):
        if path in self.routes:
            raise RuntimeError(f"Path: {path} already bind to another handler")
        self.routes[path] = handler

    def _find_handler(self, requested_path) -> tuple:
        requested_path = normalize_request_url(requested_path)
        if requested_path in self.routes:
            return self.routes[requested_path], {}

        # url that contains path variable
        for path, handler in self.routes.items():
            parsed = parse(path, requested_path)
            if parsed:
                return handler, parsed.named

        # default fallback handler
        return CommonHandlers.url_not_found_handler, {}

    def dispatch(self, http_request: Request):
        handler, kwargs = self._find_handler(http_request.path)
        return handler(http_request, **kwargs)