class Response:
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text
    def json(self):
        return {}
    def iter_lines(self):
        return []
    def close(self):
        pass

from .exceptions import RequestException

class Session:
    def __init__(self):
        self.headers = {}
    def get(self, *args, **kwargs):
        return Response()
    def post(self, *args, **kwargs):
        return Response()

__all__ = ["Session", "Response", "RequestException", "exceptions"]

class _ExceptionsModule:
    RequestException = RequestException

exceptions = _ExceptionsModule()

