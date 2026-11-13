"""Shared test settings: the tests must never contact a live server."""

import urllib.request

import pytest


@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    """Make any real download fail, so no test can reach tennisabstract.com."""
    def refuse_connection(*args, **kwargs):
        raise RuntimeError("Tests must not contact live servers; use the mock data instead")

    monkeypatch.setattr(urllib.request, "urlopen", refuse_connection)
