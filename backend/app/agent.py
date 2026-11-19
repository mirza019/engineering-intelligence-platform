from datetime import UTC, datetime
from uuid import uuid4

from backend.app.config import get_settings
from backend.app.llm import get_llm
from backend.app.rag import Retriever
from backend.app.security import UserContext
from backend.app.store import DataStore


class EngineeringAgent:
    def __init__(self, store: DataStore):
        self.store = store
        self.retriever = Retriever(store)
        self.settings = get_settings()

    async def answer(self, question: str, user: UserContext, project_id: str | None = None) -> dict:
        user.require("assistant")
        tools = ["get_project", "get_project_milestones", "get_quality_issues", "search_lessons_learned", "search_engineering_documents"]
        project = self.store.find("projects", "project_id", project_id) if project_id else None
        milestones = self.store.filter("milestones", project_id=project_id) if project_id else []
        issues = self.store.filter("quality_issues", project_id=project_id) if project_id else []
        lessons = [x for x in self.store.all("lessons_learned") if not project or x["project_type"] == project["project_type"]][:5]
        docs = self.retriever.search(question, user, project_id)
        evidence = [f"{i['ncc_id']}: {i['title']} ({i['status']})" for i in issues if i["status"] == "Open"][:5]
        evidence += [f"{m['milestone_id']}: {m['milestone_name']} — {m['status']}" for m in milestones][-3:]
        evidence += [f"{r.document['document_id']} {r.document['revision']}: {r.chunk['text']}" for r in docs]
        prompt = "Answer using only this synthetic evidence. State uncertainty.\nQuestion: " + question + "\nEvidence:\n" + "\n".join(evidence)
        answer = await get_llm(self.settings).generate(prompt)
        response_id = str(uuid4())
        sources = [{"document_id": r.document["document_id"], "revision": r.document["revision"],
                    "chunk_id": r.chunk["chunk_id"], "score": r.score} for r in docs]
        record = {"response_id": response_id, "user": user.username, "role": user.role, "timestamp": datetime.now(UTC).isoformat(),
                  "question": question, "tools_called": tools, "data_products": ["Project Master Data", "Project Milestones", "Quality Issues", "Lessons Learned", "Engineering Documents"],
                  "documents_retrieved": sources, "access_denied": False, "model": self.settings.llm_model}
        self.store.append_audit(record)
        return {"response_id": response_id, "answer": answer, "evidence": evidence, "sources": sources,
                "tools_called": tools, "lineage": ["Governed data products", "Authorized MCP tools", "Qwen response"],
                "model": self.settings.llm_model, "synthetic_data": True, "lessons_considered": len(lessons)}
