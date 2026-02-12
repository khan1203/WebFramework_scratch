import pytest

from pathlib import Path
from roob import Roob
from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter

from roob.middlewares import ErrorHandlerMiddleware
from tests.constants import BASE_URL
from tests.utils.temp_file_builder import TempFileBuilder


class TestFramework(Roob):
    def test_session(self, base_url=BASE_URL):
        session = RequestsSession()
        session.mount(
            prefix=base_url,
            adapter=RequestsWSGIAdapter(
                app=ErrorHandlerMiddleware(app=self)
            )
        )
        return session


@pytest.fixture
def app() -> TestFramework:
    cwd = Path(__file__).resolve().parent
    return TestFramework(template_dir=f"{cwd}/templates")


@pytest.fixture
def client(app: TestFramework):
    return app.test_session()

@pytest.fixture
def temp_file_builder(tmpdir_factory) -> TempFileBuilder:
    return TempFileBuilder(tmpdir_factory, root_dir="static")