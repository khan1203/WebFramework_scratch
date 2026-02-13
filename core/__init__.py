from roob.common_handlers import CommonHandlers
from roob.framework import Roob
from roob.middlewares import ErrorHandlerMiddleware
from pathlib import Path


cwd = Path(__file__).resolve().parent
app = Roob(
    template_dir=f"{cwd}/templates",
    static_dir=f"{cwd}/static"
    )

app.add_exception_handler(handler=CommonHandlers.generic_exception_handler)

exception_handler_middleware = ErrorHandlerMiddleware(
    app=app
)