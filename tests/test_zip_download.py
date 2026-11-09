import io
import os
import re
import sys
import threading
import zipfile
from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer

import pytest

import datahugger
import datahugger.__main__ as cli
from datahugger.base import DatasetDownloader
from datahugger.remotezip import HTTPRangeReader


@pytest.fixture
def zip_server():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("dataset/labels/one.xml", b"first label")
        archive.writestr("dataset/labels/two.xml", b"second label")
        archive.writestr("dataset/images/image.bin", os.urandom(2_000_000))
    payload = buffer.getvalue()
    state = {
        "ranges": [],
        "bytes": 0,
        "support_ranges": True,
        "bad_range": False,
        "payload": payload,
    }

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            payload = state["payload"]
            requested = self.headers.get("Range")
            state["ranges"].append(requested)
            if requested and state["support_ranges"]:
                match = re.fullmatch(r"bytes=(\d+)-(\d+)", requested)
                start, end = map(int, match.groups())
                body = payload[start : end + 1]
                self.send_response(206)
                actual_start = start + 1 if state["bad_range"] else start
                self.send_header(
                    "Content-Range", f"bytes {actual_start}-{end}/{len(payload)}"
                )
            else:
                body = payload
                self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            try:
                self.wfile.write(body)
                state["bytes"] += len(body)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/archive.zip"
    try:
        yield url, state, payload
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def dataset(url, **kwargs):
    downloader = DatasetDownloader("https://example.com", progress=False, **kwargs)
    downloader._files = [
        {"name": "archive.zip", "link": url, "size": None, "hash": None}
    ]
    return downloader


def test_filtered_zip_download_uses_ranges_and_preserves_paths(zip_server, tmp_path):
    url, state, payload = zip_server
    downloader = dataset(url, zip=True, filter_files=r"dataset/labels/.*\.xml")

    downloader.download(tmp_path)

    assert (tmp_path / "dataset/labels/one.xml").read_bytes() == b"first label"
    assert (tmp_path / "dataset/labels/two.xml").read_bytes() == b"second label"
    assert not (tmp_path / "dataset/images").exists()
    assert all(state["ranges"])
    assert state["bytes"] < len(payload) // 10


def test_zip_no_filter_uses_existing_full_extraction(zip_server, tmp_path):
    url, state, _ = zip_server
    dataset(url, zip=True).download(tmp_path)
    assert (tmp_path / "one.xml").read_bytes() == b"first label"
    assert state["ranges"] == [None]


def test_zip_dry_run_fetches_only_directory(zip_server, tmp_path, capsys):
    url, state, _ = zip_server
    dataset(url, zip=True, filter_files=r"dataset/labels/.*", print_only=True).download(
        tmp_path
    )
    assert "dataset/labels/one.xml" in capsys.readouterr().out
    assert not list(tmp_path.iterdir())
    assert all(state["ranges"])
    assert len(state["ranges"]) == 4  # probe and ZIP directory reads, no members


def test_zip_no_filter_dry_run_does_not_download(zip_server, tmp_path, capsys):
    url, state, _ = zip_server
    dataset(url, zip=True, print_only=True).download(tmp_path)
    assert "archive.zip" in capsys.readouterr().out
    assert state["ranges"] == []


def test_zip_no_range_support_fails_without_reading_archive(zip_server, tmp_path):
    url, state, _ = zip_server
    state["support_ranges"] = False
    with pytest.raises(OSError, match="did not honor"):
        dataset(url, zip=True, filter_files=".*").download(tmp_path)
    assert state["ranges"] == ["bytes=0-0"]
    assert not list(tmp_path.iterdir())


def test_zip_invalid_content_range_is_rejected(zip_server):
    url, state, _ = zip_server
    state["bad_range"] = True
    with pytest.raises(OSError, match="Content-Range"):
        HTTPRangeReader(url)


def test_zip_size_and_overwrite_options(zip_server, tmp_path):
    url, _, _ = zip_server
    first = tmp_path / "dataset/labels/one.xml"
    first.parent.mkdir(parents=True)
    first.write_bytes(b"existing")
    dataset(
        url, zip=True, filter_files=r"dataset/labels/.*", max_file_size=12
    ).download(tmp_path)
    assert first.read_bytes() == b"existing"
    assert not (first.parent / "two.xml").exists()
    dataset(
        url, zip=True, filter_files=r"dataset/labels/one\.xml", force_download=True
    ).download(tmp_path)
    assert first.read_bytes() == b"first label"


def test_zip_filter_no_matches(zip_server, tmp_path):
    url, _, _ = zip_server
    dataset(url, zip=True, filter_files=r"missing/.*").download(tmp_path)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("filename", ["../outside.txt", "/absolute.txt", "a\\b.txt"])
def test_zip_rejects_unsafe_paths(zip_server, tmp_path, filename):
    url, state, _ = zip_server
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(filename, b"unsafe")
    state["payload"] = buffer.getvalue()
    with pytest.raises(ValueError, match="Unsafe ZIP member path"):
        dataset(url, zip=True, filter_files=".*").download(tmp_path / "output")
    assert not (tmp_path / "outside.txt").exists()


def test_zip_rejects_symlink_outside_output(zip_server, tmp_path):
    url, _, _ = zip_server
    outside = tmp_path / "outside"
    outside.mkdir()
    root = tmp_path / "output"
    root.mkdir()
    (root / "dataset").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="Unsafe ZIP member path"):
        dataset(url, zip=True, filter_files=r"dataset/labels/.*").download(root)
    assert not list(outside.iterdir())


def test_zip_corrupt_member_does_not_replace_existing_file(zip_server, tmp_path):
    url, state, _ = zip_server
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("one.txt", b"original content")
    state["payload"] = buffer.getvalue().replace(
        b"original content", b"corrupt! content"
    )
    destination = tmp_path / "one.txt"
    destination.write_bytes(b"existing")
    with pytest.raises(zipfile.BadZipFile, match="CRC"):
        dataset(url, zip=True, filter_files=".*", force_download=True).download(
            tmp_path
        )
    assert destination.read_bytes() == b"existing"
    assert list(tmp_path.iterdir()) == [destination]


def test_zip_rejects_conflicting_options(zip_server, tmp_path):
    url, state, _ = zip_server
    with pytest.raises(ValueError, match="unzip=False"):
        dataset(url, zip=True, unzip=False)
    with pytest.raises(ValueError, match="checksum"):
        dataset(url, zip=True, filter_files=".*", checksum=True).download(tmp_path)
    assert state["ranges"] == []


@pytest.mark.parametrize("flag", ["-z", "--zip"])
def test_cli_zip_option(monkeypatch, tmp_path, flag):
    calls = []
    monkeypatch.setattr(
        cli, "get", lambda *args, **kwargs: calls.append((args, kwargs))
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["datahugger", "10.1/example", str(tmp_path), flag, "--filter-files", ".*"],
    )
    cli.main()
    assert calls[0][1]["zip"] is True
    assert calls[0][1]["filter_files"] == ".*"


def test_python_api_passes_zip(monkeypatch):
    calls = []

    def service(resource, **kwargs):
        calls.append(kwargs)
        return object()

    monkeypatch.setattr("datahugger.api.parse_resource_identifier", lambda value: value)
    monkeypatch.setattr("datahugger.api._resolve_service", lambda value: service)
    datahugger.info("resource", zip=True)
    assert calls[0]["zip"] is True
