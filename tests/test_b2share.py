from unittest.mock import Mock

import datahugger.services as services


def test_b2share_resolves_legacy_id_and_reads_v3_file_entries(monkeypatch):
    requests = []
    responses = {
        "https://b2share.eudat.eu/api/records": {
            "hits": {
                "hits": [
                    {
                        "id": "24x1a-xgx60",
                        "links": {
                            "doi": "https://doi.org/10.23728/b2share.db2ef5890fa44c7a85af366a50de73b9",
                            "files": "https://b2share.eudat.eu/api/records/24x1a-xgx60/files",
                        },
                    }
                ]
            }
        },
        "https://b2share.eudat.eu/api/records/24x1a-xgx60/files": {
            "entries": [
                {
                    "key": "2024-02-13.sav",
                    "size": 42,
                    "checksum": "md5:abc123",
                    "links": {
                        "content": "https://b2share.eudat.eu/api/records/24x1a-xgx60/files/2024-02-13.sav/content"
                    },
                }
            ]
        },
    }

    def get(url, params=None):
        requests.append((url, params))
        response = Mock()
        response.json.return_value = responses[url]
        response.raise_for_status.return_value = None
        return response

    monkeypatch.setattr(services.requests, "get", get)
    dataset = services.B2shareDataset(
        "https://b2share.eudat.eu/records/db2ef5890fa44c7a85af366a50de73b9"
    )

    assert dataset.files == [
        {
            "link": "https://b2share.eudat.eu/api/records/24x1a-xgx60/files/2024-02-13.sav/content",
            "name": "2024-02-13.sav",
            "size": 42,
            "hash": "abc123",
            "hash_type": "md5",
        }
    ]
    assert requests[0] == (
        "https://b2share.eudat.eu/api/records",
        {"q": "db2ef5890fa44c7a85af366a50de73b9"},
    )
