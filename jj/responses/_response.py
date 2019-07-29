import io
from http.cookies import Morsel
from json import dumps
from typing import Any, Dict, List, MutableMapping, Optional, Tuple, Union
from unittest.mock import sentinel as nil

from aiohttp import web
from aiohttp.payload import BytesPayload, IOBasePayload, TextIOPayload
from aiohttp.web import ContentCoding
from packed import packable

from ._stream_response import StreamResponse

__all__ = ("Response",)


@packable("jj.responses.Response")
class Response(web.Response, StreamResponse):
    def __init__(self, *,
                 json: Any = nil,
                 body: Optional[Union[str, bytes]] = None,
                 text: Optional[str] = None,
                 status: int = 200,
                 reason: Optional[str] = None,
                 headers: Optional[MutableMapping[str, str]] = None) -> None:
        headers = headers or {}

        if json is not nil:
            assert (body is None) and (text is None)
            body = dumps(json)
            headers.update({"Content-Type": "application/json"})

        if (body is None) and (text is None):
            body = ""

        if isinstance(body, io.IOBase):
            headers.update({"Content-Disposition": "inline"})

        super().__init__(body=body, text=text, status=status, reason=reason, headers=headers)

    @property
    def content_coding(self) -> Optional[ContentCoding]:
        return self._compression_force

    def _cookie_to_dict(self, cookie: "Morsel[str]") -> Dict[str, Union[str, None]]:
        dictionary: Dict[str, Union[str, None]] = {
            "name": cookie.key,
            "value": cookie.value,
        }
        for attr in ("expires", "domain", "max-age", "path", "secure", "httponly", "version"):
            key = attr.replace("-", "_")
            val = cookie.get(attr)
            dictionary[key] = None if val == "" else val
        return dictionary

    def copy(self) -> "Response":
        assert not self.prepared

        response = self.__class__(status=self.status, reason=self.reason,  # type: ignore
                                  headers=self.headers, body=self.body)
        for cookie in self.cookies.values():
            response.set_cookie(**self._cookie_to_dict(cookie))  # type: ignore
        if self.chunked:
            response.enable_chunked_encoding()
        if self._compression_force:
            response.enable_compression(self._compression_force)
        return response

    def __packed__(self) -> Dict[str, Any]:
        assert not self.prepared

        headers = [[key, val] for key, val in self.headers.items()]
        cookies = [self._cookie_to_dict(cookie) for cookie in self.cookies.values()]

        compression = self._compression_force
        if isinstance(compression, ContentCoding):
            compression = compression.value

        if self.body is None:
            body = self.body
        elif isinstance(self.body, (bytes, bytearray, memoryview)):
            body = bytes(self.body)
        elif isinstance(self.body, BytesPayload):
            body = bytes(self.body._value)
        elif isinstance(self.body, TextIOPayload):
            body = bytes(self.body._value.read(), self.body.encoding)  # type: ignore
        elif isinstance(self.body, IOBasePayload):
            body = bytes(self.body._value.read())
        else:
            raise ValueError()

        return {
            "status": self.status,
            "reason": self.reason,
            "headers": headers,
            "cookies": cookies,
            "body": body,
            "chunked": self.chunked,
            "compression": compression,
        }

    @classmethod
    def __unpacked__(cls, *,
                     status: int,
                     reason: Optional[str],
                     headers: List[Tuple[str, str]],
                     cookies: List[Dict[str, Union[str, None]]],
                     body: Optional[bytes],
                     chunked: bool,
                     compression: Optional[ContentCoding],
                     **kwargs: Any) -> "Response":
        response = cls(status=status, reason=reason, headers=headers, body=body)  # type: ignore
        for cookie in cookies:
            response.set_cookie(**cookie)  # type: ignore
        if compression:
            response.enable_compression(compression)
        if chunked:
            response.enable_chunked_encoding()
        return response
