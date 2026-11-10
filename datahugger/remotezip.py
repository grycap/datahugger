"""Seekable HTTP reader for accessing ZIP members without a full download."""

import io
import re

import requests


class HTTPRangeReader(io.RawIOBase):
    """Seekable HTTP reader that limits each range response to 64 KiB.

    ``read()`` still returns the requested bytes, so a caller requesting a large
    result necessarily receives a correspondingly large bytes object.
    """

    block_size = 64 * 1024

    def __init__(self, url, session=None):
        super().__init__()
        self.url = url
        self.session = session if session is not None else requests.Session()
        self.position = 0
        self.size = None
        self.validator = None
        self._get_range(0, 0)

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            position = offset
        elif whence == io.SEEK_CUR:
            position = self.position + offset
        elif whence == io.SEEK_END:
            position = self.size + offset
        else:
            raise ValueError(f"Invalid whence: {whence}")
        if position < 0:
            raise ValueError("Negative seek position")
        self.position = position
        return position

    def read(self, size=-1):
        if self.size is None:
            raise OSError("The ZIP size is unknown.")
        if size is None or size < 0:
            size = self.size - self.position
        size = min(size, self.size - self.position)
        if size <= 0:
            return b""

        data = bytearray()
        start = self.position
        end = self.position + size
        while start < end:
            chunk_size = min(self.block_size, end - start)
            data.extend(self._get_range(start, start + chunk_size - 1))
            start += chunk_size
        self.position += len(data)
        return bytes(data)

    def _get_range(self, start, end):
        headers = {
            "Range": f"bytes={start}-{end}",
            "Accept-Encoding": "identity",
        }
        if self.validator:
            headers["If-Range"] = self.validator
        with self.session.get(
            self.url, headers=headers, stream=True, timeout=(10, 30)
        ) as response:
            response.raise_for_status()
            if response.status_code != 206:
                raise OSError(
                    "The ZIP server did not honor the HTTP range request "
                    "(or the ZIP changed during download)."
                )
            content_range = response.headers.get("Content-Range", "")
            match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", content_range)
            if not match or int(match.group(1)) != start or int(match.group(2)) != end:
                raise OSError(f"Invalid HTTP Content-Range: {content_range!r}")
            total = int(match.group(3))
            if total <= end or (self.size is not None and total != self.size):
                raise OSError("The ZIP size changed or the HTTP range is invalid.")
            if (
                response.headers.get("Content-Encoding", "identity").lower()
                != "identity"
            ):
                raise OSError("The ZIP server returned an encoded HTTP range.")
            if self.validator:
                etag = response.headers.get("ETag")
                modified = response.headers.get("Last-Modified")
                current = etag if self.validator.startswith('"') else modified
                if current is not None and current != self.validator:
                    raise OSError("The ZIP validator changed during download.")
            if self.size is None:
                self.size = total
                etag = response.headers.get("ETag")
                if etag and not etag.startswith("W/"):
                    self.validator = etag
                else:
                    self.validator = response.headers.get("Last-Modified")
            data = response.raw.read(end - start + 2, decode_content=False)
            if len(data) != end - start + 1:
                raise OSError("The ZIP server returned an incomplete HTTP range.")
            return data
