from unittest.mock import Mock

import requests

from datahugger.base import DatasetDownloader


class TokenTestDownloader(DatasetDownloader):
    API_URL = "https://example.test"
    API_URL_META = "{api_url}/metadata"
    REGEXP_ID = r"(?P<id>dataset)"
    META_FILES_JSONPATH = "$.files[*]"
    ATTR_NAME_JSONPATH = "$.name"
    ATTR_FILE_LINK_JSONPATH = "$.url"
    ATTR_SIZE_JSONPATH = "$.size"


def test_token_is_kept_on_session_and_used_for_metadata_and_download(monkeypatch, tmp_path):
    session = Mock(spec=requests.Session)
    session.headers = {}
    metadata_response = Mock()
    metadata_response.raise_for_status.return_value = None
    metadata_response.json.return_value = {
        "files": [{"name": "data.txt", "url": "https://example.test/data.txt", "size": 4}]
    }
    download_response = Mock()
    download_response.raise_for_status.return_value = None
    download_response.headers = {"content-length": "4"}
    download_response.content = b"data"
    session.get.side_effect = [metadata_response, download_response]
    session_factory = Mock(return_value=session)
    monkeypatch.setattr(requests, "Session", session_factory)

    downloader = TokenTestDownloader(
        "https://example.test/dataset", token="secret-token", progress=False
    )

    assert downloader.session is session
    assert session.headers["Authorization"] == "Bearer secret-token"
    assert downloader.files[0]["name"] == "data.txt"
    downloader.download_file(
        "https://example.test/data.txt", tmp_path, "data.txt", file_size=4
    )

    assert session_factory.call_count == 1
    assert [call.args[0] for call in session.get.call_args_list] == [
        "https://example.test/metadata",
        "https://example.test/data.txt",
    ]
    assert (tmp_path / "data.txt").read_bytes() == b"data"


def test_session_has_no_authorization_header_without_token(monkeypatch):
    session = requests.Session()
    monkeypatch.setattr(requests, "Session", Mock(return_value=session))

    downloader = TokenTestDownloader("https://example.test/dataset")

    assert "Authorization" not in downloader.session.headers
