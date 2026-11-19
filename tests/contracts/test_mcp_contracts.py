import pytest

from backend.app.rag import Retriever
from backend.app.security import Role, UserContext
from backend.app.store import store


def test_retriever_never_returns_obsolete_revisions():
    results = Retriever(store).search("interface verification", UserContext("engineer", Role.ENGINEER))
    assert results
    assert all(r.document["is_current"] and r.document["revision_status"] == "Released" for r in results)


def test_supplier_authorization_happens_before_search():
    results = Retriever(store).search("interface", UserContext("supplier", Role.SUPPLIER))
    assert all(r.document["classification"] == "external" for r in results)


def test_supplier_lessons_permission_denied():
    with pytest.raises(Exception):
        UserContext("supplier", Role.SUPPLIER).require("lessons")
