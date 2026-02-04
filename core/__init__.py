from roob.framework import Roob
from roob.middlewares import ErrorHandlerMiddleware
from roob.common_handlers import CommonHandlers


app = Roob()
exception_handler_middleware = ErrorHandlerMiddleware(
    app=app
)