from datetime import UTC, datetime
from typing import Any

from backend.app.store import DataStore


def quality_results(store: DataStore) -> list[dict[str, Any]]:
    projects = {p["project_id"] for p in store.all("projects")}
    equipment = {e["equipment_id"] for e in store.all("equipment")}
    documents = store.all("engineering_documents")
    rules = [
        ("project_id_not_null", all(p.get("project_id") for p in store.all("projects")), "Project Master Data"),
        ("milestone_project_fk", all(m.get("project_id") in projects for m in store.all("milestones")), "Project Milestones"),
        ("ncc_project_fk", all(q.get("project_id") in projects and q.get("equipment_id") in equipment for q in store.all("quality_issues")), "Quality Issues"),
        ("planned_date_valid", all(len(m.get("planned_date", "")) == 10 for m in store.all("milestones")), "Project Milestones"),
        ("released_revision_present", all(d.get("revision") for d in documents if d.get("revision_status") == "Released"), "Engineering Documents"),
        ("one_current_revision", _one_current(documents), "Engineering Documents"),
    ]
    checked = datetime.now(UTC).isoformat()
    return [{"rule_name": name, "data_product": product, "passed": passed, "checked_at": checked,
             "details": "Rule passed" if passed else "Rule failed"} for name, passed, product in rules]


def _one_current(documents: list[dict[str, Any]]) -> bool:
    ids = {d["document_id"] for d in documents}
    return all(sum(1 for d in documents if d["document_id"] == doc_id and d["is_current"] and d["revision_status"] == "Released") == 1 for doc_id in ids)
