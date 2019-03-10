import mimetypes
from pathlib import Path
from typing import Union, Optional, MutableMapping

from aiohttp import web

from ._stream_response import StreamResponse


__all__ = ("StaticResponse",)


class StaticResponse(web.FileResponse, StreamResponse):
    def __init__(self, path: Union[str, Path], *,
                 chunk_size: int = 256 * 1024,
                 headers: Optional[MutableMapping[str, str]] = None) -> None:
        mimetypes.add_type("application/json", ".json")
        super().__init__(path, chunk_size, headers=headers)
