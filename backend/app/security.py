from dataclasses import dataclass
from enum import StrEnum

from fastapi import Header, HTTPException


class Role(StrEnum):
    ENGINEER = "engineer"
    PROJECT_MANAGER = "project_manager"
    QUALITY_MANAGER = "quality_manager"
    SUPPLIER = "supplier"


PERMISSIONS: dict[Role, set[str]] = {
    Role.ENGINEER: {"projects", "milestones", "equipment", "quality", "documents", "lessons", "governance", "lineage", "assistant"},
    Role.PROJECT_MANAGER: {"projects", "milestones", "equipment", "quality", "documents", "lessons", "governance", "lineage", "assistant", "audit"},
    Role.QUALITY_MANAGER: {"projects", "milestones", "equipment", "quality", "documents", "lessons", "governance", "lineage", "assistant", "audit"},
    Role.SUPPLIER: {"projects", "milestones", "equipment", "external_documents"},
}


@dataclass(frozen=True)
class UserContext:
    username: str
    role: Role

    def require(self, resource: str) -> None:
        if resource not in PERMISSIONS[self.role]:
            raise HTTPException(status_code=403, detail=f"Role '{self.role}' cannot access {resource}")


def get_user(
    x_user: str = Header(default="demo.engineer"),
    x_role: Role = Header(default=Role.ENGINEER),
) -> UserContext:
    return UserContext(username=x_user, role=x_role)
