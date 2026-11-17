from types import SimpleNamespace

from datahugger.services import ArXivDataset
from datahugger.services import DESYDataset
from datahugger.services import DataOneDataset
from datahugger.services import PangaeaDataset


def test_arxiv_uses_repository_file_adapter_for_public_listing():
    dataset = ArXivDataset("https://arxiv.org/abs/astro-ph/9802301v1")

    assert dataset.files == [
        {
            "link": "https://arxiv.org/pdf/astro-ph/9802301v1.pdf",
            "name": "9802301v1.pdf",
            "size": None,
            "hash": None,
            "hash_type": None,
        }
    ]


def test_dataone_uses_repository_file_adapter_for_public_listing(monkeypatch):
    xml = b"""<resultset><dataset>
      <otherEntity>
        <entityName>sample.csv</entityName>
        <physical><size>12</size><distribution><online>
          <url function="download">https://example.org/sample.csv</url>
        </online></distribution></physical>
      </otherEntity>
    </dataset></resultset>"""

    monkeypatch.setattr(
        "datahugger.services.requests.get",
        lambda url: SimpleNamespace(content=xml, raise_for_status=lambda: None),
    )
    dataset = DataOneDataset("https://arcticdata.io/view/doi:10.18739/A2KH0DZ42")

    assert dataset.files[0]["name"] == "sample.csv"


def test_pangaea_uses_repository_file_adapter_for_public_listing(monkeypatch):
    def get(url):
        return SimpleNamespace(
            json=lambda: {
                "distribution": {
                    "encodingFormat": "application/zip",
                    "contentUrl": "https://example.org/data.zip",
                }
            },
            raise_for_status=lambda: None,
        )

    def head(url):
        return SimpleNamespace(
            headers={"content-disposition": 'attachment; filename="data.zip"'}
        )

    monkeypatch.setattr("datahugger.services.requests.get", get)
    monkeypatch.setattr("datahugger.services.requests.head", head)
    dataset = PangaeaDataset("https://doi.pangaea.de/10.1594/PANGAEA.893034")

    assert dataset.files[0]["name"] == '"data.zip"'


def test_desy_uses_repository_file_adapter_for_public_listing(monkeypatch):
    xml = b"""<metalink xmlns="urn:ietf:params:xml:ns:metalink">
      <file name="environment.yml">
        <url>https://example.org/environment.yml</url>
        <size>12</size>
      </file>
    </metalink>"""
    monkeypatch.setattr(
        "datahugger.services.requests.get",
        lambda *args, **kwargs: SimpleNamespace(
            content=xml, raise_for_status=lambda: None
        ),
    )
    dataset = DESYDataset("https://public-doi.desy.de/detail/example-id")

    assert dataset.files[0]["name"] == "environment.yml"
    assert dataset.files[0]["size"] == 12
