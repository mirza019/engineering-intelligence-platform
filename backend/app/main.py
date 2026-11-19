from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.agent import EngineeringAgent
from backend.app.config import get_settings
from backend.app.governance import quality_results
from backend.app.rag import Retriever
from backend.app.security import Role, UserContext, get_user
from backend.app.store import store

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(","), allow_methods=["*"], allow_headers=["*"])


class Question(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    project_id: str | None = None


def _require(user: UserContext, resource: str):
    user.require(resource)
    return user


@app.get("/health")
def health():
    return {"status": "ok", "model": settings.llm_model, "data": "synthetic"}


@app.get("/api/dashboard")
def dashboard(user: UserContext = Depends(get_user)):
    _require(user, "projects")
    return {"projects": len(store.all("projects")), "open_issues": sum(x["status"] == "Open" for x in store.all("quality_issues")),
            "at_risk_milestones": sum(x["status"] == "At Risk" for x in store.all("milestones")),
            "released_documents": sum(x["revision_status"] == "Released" for x in store.all("engineering_documents")),
            "quality_pass_rate": round(sum(x["passed"] for x in quality_results(store)) / len(quality_results(store)) * 100)}


@app.get("/api/projects")
def projects(user: UserContext = Depends(get_user)):
    _require(user, "projects")
    return store.all("projects")


@app.get("/api/projects/{project_id}")
def project_detail(project_id: str, user: UserContext = Depends(get_user)):
    _require(user, "projects")
    project = store.find("projects", "project_id", project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return {**project, "milestones": store.filter("milestones", project_id=project_id),
            "equipment": store.filter("equipment", project_id=project_id),
            "quality_issues": [] if user.role == Role.SUPPLIER else store.filter("quality_issues", project_id=project_id),
            "documents": [d for d in store.filter("engineering_documents", project_id=project_id)
                          if d["is_current"] and (user.role != Role.SUPPLIER or d["classification"] == "external")]}


@app.get("/api/quality-issues")
def issues(user: UserContext = Depends(get_user)):
    _require(user, "quality")
    return store.all("quality_issues")


@app.get("/api/lessons")
def lessons(user: UserContext = Depends(get_user)):
    _require(user, "lessons")
    return store.all("lessons_learned")


@app.get("/api/documents")
def documents(historical: bool = False, user: UserContext = Depends(get_user)):
    _require(user, "documents" if user.role != Role.SUPPLIER else "external_documents")
    return [d for d in store.all("engineering_documents") if (historical or d["is_current"])
            and (user.role != Role.SUPPLIER or d["classification"] == "external")]


@app.get("/api/documents/{document_id}/latest")
def latest_document(document_id: str, user: UserContext = Depends(get_user)):
    docs = documents(False, user)
    doc = next((d for d in docs if d["document_id"] == document_id and d["revision_status"] == "Released"), None)
    if not doc:
        raise HTTPException(404, "Released document not found")
    return doc


@app.get("/api/search")
def search(q: str = Query(min_length=2), project_id: str | None = None, user: UserContext = Depends(get_user)):
    results = Retriever(store).search(q, user, project_id)
    return [{"score": r.score, "document": r.document, "chunk": r.chunk} for r in results]


@app.get("/api/governance")
def governance(user: UserContext = Depends(get_user)):
    _require(user, "governance")
    return store.all("governance")


@app.get("/api/lineage")
def lineage(user: UserContext = Depends(get_user)):
    _require(user, "lineage")
    return store.all("lineage")


@app.get("/api/quality-results")
def data_quality(user: UserContext = Depends(get_user)):
    _require(user, "governance")
    return quality_results(store)


@app.get("/api/audit")
def audit(user: UserContext = Depends(get_user)):
    _require(user, "audit")
    return store.all("audit_log")


@app.post("/api/assistant")
async def assistant(payload: Question, user: UserContext = Depends(get_user)):
    return await EngineeringAgent(store).answer(payload.question, user, payload.project_id)
