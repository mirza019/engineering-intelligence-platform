from mcp.server.fastmcp import FastMCP

from backend.app.rag import Retriever
from backend.app.security import Role, UserContext
from backend.app.store import store

mcp = FastMCP("Engineering Intelligence MCP")


def _user(role: str, username: str = "mcp.user") -> UserContext:
    return UserContext(username=username, role=Role(role))


@mcp.tool()
def get_project(project_id: str, role: str = "engineer") -> dict:
    user = _user(role); user.require("projects")
    return store.find("projects", "project_id", project_id) or {"error": "not found"}


@mcp.tool()
def get_project_milestones(project_id: str, role: str = "engineer") -> list[dict]:
    user = _user(role); user.require("milestones")
    return store.filter("milestones", project_id=project_id)


@mcp.tool()
def get_quality_issues(project_id: str, role: str = "engineer") -> list[dict]:
    user = _user(role); user.require("quality")
    return store.filter("quality_issues", project_id=project_id)


@mcp.tool()
def get_equipment(project_id: str, role: str = "engineer") -> list[dict]:
    user = _user(role); user.require("equipment")
    return store.filter("equipment", project_id=project_id)


@mcp.tool()
def get_latest_document(document_id: str, role: str = "engineer") -> dict:
    user = _user(role)
    user.require("documents" if user.role != Role.SUPPLIER else "external_documents")
    docs = [d for d in store.filter("engineering_documents", document_id=document_id)
            if d["is_current"] and d["revision_status"] == "Released"]
    docs = [d for d in docs if user.role != Role.SUPPLIER or d["classification"] == "external"]
    return docs[0] if docs else {"error": "not found or forbidden"}


@mcp.tool()
def search_engineering_documents(query: str, project_id: str | None = None, role: str = "engineer") -> list[dict]:
    results = Retriever(store).search(query, _user(role), project_id)
    return [{"score": r.score, "document": r.document, "chunk": r.chunk} for r in results]


@mcp.tool()
def search_lessons_learned(query: str, project_type: str | None = None, role: str = "engineer") -> list[dict]:
    user = _user(role); user.require("lessons")
    terms = query.lower().split()
    return [x for x in store.all("lessons_learned") if (not project_type or x["project_type"] == project_type)
            and any(t in f"{x['problem']} {x['root_cause']} {x['recommendation']}".lower() for t in terms)][:10]


@mcp.tool()
def get_data_lineage(data_product: str, role: str = "engineer") -> dict:
    user = _user(role); user.require("lineage")
    return store.find("lineage", "data_product", data_product) or {"error": "not found"}


if __name__ == "__main__":
    mcp.run()
