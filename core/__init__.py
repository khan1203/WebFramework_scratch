from roob.framework import Roob
from roob.middlewares import ErrorHandlerMiddleware
from pathlib import Path


cwd = Path(__file__).resolve().parent
app = Roob(template_dir=f"{cwd}/templates")

exception_handler_middleware = ErrorHandlerMiddleware(
    app=app
)