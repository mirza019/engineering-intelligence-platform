import json
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Any

SEED = 20261119


def _iso(day: date) -> str:
    return day.isoformat()


def generate_data(seed: int = SEED) -> dict[str, list[dict[str, Any]]]:
    rng = random.Random(seed)
    countries = ["Germany", "Denmark", "Netherlands", "Spain", "Poland", "Finland"]
    types = ["Wind Integration", "Grid Modernization", "Hydrogen", "Substation", "Storage"]
    equipment_types = ["Transformer", "Compressor", "Converter", "Turbine", "Switchgear"]
    statuses = ["Planning", "Execution", "Commissioning", "Completed"]
    projects = []
    milestones = []
    equipment = []
    issues = []
    lessons = []
    documents = []
    chunks = []
    base = date(2024, 1, 15)
    for i in range(1, 21):
        pid = f"P{1000+i}"
        start = base + timedelta(days=i * 17)
        ptype = types[(i - 1) % len(types)]
        projects.append({
            "project_id": pid, "project_name": f"Aurora {ptype} {i:02d}",
            "customer": f"Synthetic Utility {chr(64+i)}", "country": countries[i % len(countries)],
            "project_manager": f"Manager {i:02d}", "project_status": statuses[i % 4],
            "project_type": ptype, "start_date": _iso(start),
            "planned_completion_date": _iso(start + timedelta(days=540 + i * 3)),
        })
        for m in range(1, 6):
            planned = start + timedelta(days=m * 90)
            milestones.append({"milestone_id": f"M{i:02d}{m:02d}", "project_id": pid,
                "milestone_name": ["Design Freeze", "Procurement", "Factory Test", "Site Readiness", "Handover"][m-1],
                "planned_date": _iso(planned), "actual_date": _iso(planned + timedelta(days=rng.randint(-8, 30))) if m < 4 else None,
                "status": "Completed" if m < 4 else ("At Risk" if (i+m) % 4 == 0 else "Planned")})
        for e in range(1, 4):
            etype = equipment_types[(i + e) % len(equipment_types)]
            equipment.append({"equipment_id": f"E{i:02d}{e:02d}", "project_id": pid, "equipment_type": etype,
                "manufacturer": f"Synthetic Works {e}", "specification": f"{etype} rated for synthetic project duty",
                "status": ["Designed", "Ordered", "Installed"][(i+e) % 3]})
    for i in range(1, 51):
        project = projects[(i - 1) % len(projects)]
        eq = next(e for e in equipment if e["project_id"] == project["project_id"])
        opened = base + timedelta(days=i * 9)
        issue = {
            "ncc_id": f"NCC-{i:04d}", "project_id": project["project_id"], "equipment_id": eq["equipment_id"],
            "title": f"{eq['equipment_type']} interface deviation {i}",
            "description": "Synthetic inspection identified a dimensional or documentation mismatch at an interface.",
            "severity": ["Low", "Medium", "High", "Critical"][i % 4],
            "root_cause": ["Requirement ambiguity", "Supplier process variation", "Late design change"][i % 3],
            "corrective_action": "Verify interface, update controlled documentation, and record acceptance evidence.",
            "status": "Closed" if i % 3 == 0 else "Open", "opened_date": _iso(opened),
            "closed_date": _iso(opened + timedelta(days=21)) if i % 3 == 0 else None,
            "classification": "internal",
        }
        issues.append(issue)
        lessons.append({"lesson_id": f"LL-{i:04d}", "project_type": project["project_type"],
            "equipment_type": eq["equipment_type"], "problem": issue["title"], "root_cause": issue["root_cause"],
            "impact": "Potential schedule delay and rework", "recommendation": "Freeze interfaces early and add supplier evidence gates.",
            "source_project": project["project_id"], "date": _iso(opened + timedelta(days=30)), "classification": "internal"})
    for i in range(1, 31):
        project = projects[(i - 1) % 20]
        eq = next(e for e in equipment if e["project_id"] == project["project_id"])
        doc_id = f"SPEC-{i:03d}"
        for rev in range(1, 4):
            current = rev == 3
            record = {"revision_id": f"{doc_id}-R{rev:02d}", "document_id": doc_id,
                "project_id": project["project_id"], "equipment_id": eq["equipment_id"],
                "title": f"{eq['equipment_type']} Engineering Specification", "document_type": "Specification",
                "revision": f"R{rev:02d}", "revision_status": "Released" if current else "Obsolete",
                "is_current": current, "classification": "external" if i % 5 == 0 else "internal",
                "created_date": _iso(base + timedelta(days=i * 8 + rev))}
            documents.append(record)
            chunks.append({"chunk_id": f"{record['revision_id']}-C01", "revision_id": record["revision_id"],
                "text": f"Synthetic {eq['equipment_type']} specification revision {rev}. Interface verification, quality evidence, and commissioning checks are required."})
    governance = [
        {"data_product_name": name, "business_owner": owner, "data_steward": "Data Governance Lead",
         "authoritative_source": source, "classification": classification, "quality_status": "Passed",
         "last_updated": "2026-11-19", "retention_rule": "7 years", "allowed_roles": roles}
        for name, owner, source, classification, roles in [
            ("Project Master Data", "PMO Director", "Project Registry", "internal", ["engineer","project_manager","quality_manager","supplier"]),
            ("Project Milestones", "PMO Director", "Schedule Control", "internal", ["engineer","project_manager","quality_manager","supplier"]),
            ("Quality Issues", "Quality Director", "Quality Management System", "confidential", ["engineer","project_manager","quality_manager"]),
            ("Engineering Documents", "Engineering Director", "Document Management System", "mixed", ["engineer","project_manager","quality_manager","supplier"]),
            ("Lessons Learned", "Engineering Director", "Lessons Repository", "internal", ["engineer","project_manager","quality_manager"]),
        ]]
    lineage = [{"data_product": g["data_product_name"], "nodes": [g["authoritative_source"], "Raw ingestion", "Validated transformation", g["data_product_name"], "API / MCP", "AI response"]} for g in governance]
    return {"projects": projects, "milestones": milestones, "equipment": equipment, "quality_issues": issues,
            "lessons_learned": lessons, "engineering_documents": documents, "document_chunks": chunks,
            "governance": governance, "lineage": lineage, "audit_log": []}


def write_data(path: str | Path, seed: int = SEED) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(generate_data(seed), indent=2), encoding="utf-8")
    return target


if __name__ == "__main__":
    write_data("data/generated/platform_data.json")
