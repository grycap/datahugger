import pytest

import datahugger
from datahugger.api import _resolve_service
from datahugger.handles import DOI
from datahugger.handles import ArXiv
from datahugger.services import DataDryadDataset
from datahugger.services import DataverseDataset


def test_dryad_stash_dataset_url_parsing():
    service = DataDryadDataset(
        "https://datadryad.org/stash/dataset/doi:10.5061/dryad.31zcrjdm5"
    )

    assert service._params == {"record_id": "10.5061/dryad.31zcrjdm5"}


def test_dataverse_citation_url_parsing():
    service = DataverseDataset(
        "https://dataverse.harvard.edu/citation?persistentId="
        "doi:10.7910/DVN/KBHLOD"
    )

    assert service._params == {
        "type": None,
        "record_id": "doi:10.7910/DVN/KBHLOD",
    }
    assert service.API_URL_META.format(
        base_url="https://dataverse.harvard.edu", **service._params
    ) == (
        "https://dataverse.harvard.edu/api/datasets/:persistentId/versions/"
        ":latest-published/?persistentId=doi:10.7910/DVN/KBHLOD"
    )


def test_resolve_service():
    doi = DOI.parse("10.34894/FXUGHW")
    doi.resolve()

    service = _resolve_service(doi)(doi)

    assert isinstance(service, DataverseDataset)


@pytest.mark.xfail(raises=ValueError)
def test_doi_not_found(tmpdir):
    doi = "10.1038/s42256-020-00287"

    datahugger.get(doi, tmpdir)


def test_resolve_service_via_doi_handle(tmpdir):
    doi = DOI.parse("10.34894/FXUGHW")
    doi.resolve()

    r = datahugger.get(doi, tmpdir)

    assert isinstance(doi, DOI)
    assert isinstance(r.dataset, DataverseDataset)


def test_get_doi_metadata_cls(tmpdir):
    doi = DOI.parse("10.34894/FXUGHW")
    doi.resolve()

    m = doi.metadata.cls()

    assert isinstance(m, dict)


def test_get_doi_metadata_bibtex(tmpdir):
    doi = DOI.parse("10.34894/FXUGHW")
    doi.resolve()

    m = doi.metadata.bibtex()

    assert isinstance(m, str)


def test_arxiv_handle(tmpdir):
    arxiv = ArXiv.parse("https://arxiv.org/abs/astro-ph/9802301v1")

    m = arxiv.metadata.cls()

    assert isinstance(m, dict)


def test_get_doi_metadata_from_instance(tmpdir):
    # initiate datahugger downloader and then get metadata
    service = datahugger.info("10.34894/FXUGHW")
    m1 = service.resource.metadata.citation()

    # initiate datahugger resource and get metadata
    doi = DOI.parse("10.34894/FXUGHW")
    doi.resolve()
    m2 = doi.metadata.citation()

    assert m1 == m2 is not None
