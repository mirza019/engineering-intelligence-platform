# Delivery roadmap

## Phase 1 — Database and synthetic data

- Model projects, milestones, equipment, quality issues, lessons learned, and revisioned engineering documents.
- Separate document revision metadata from chunks.
- Add PostgreSQL + pgvector migration tooling.
- Generate deterministic synthetic data at or above the requested volumes.
- Test referential integrity, revision invariants, dates, and synthetic-data counts.

## Phase 2 — FastAPI

- Add typed API schemas, health checks, service boundaries, and resource endpoints.

## Phase 3 — Governance and quality

- Add data-product ownership, classification, authoritative sources, allowed roles, lineage, and persisted quality results.

## Phase 4 — RAG

- Add extraction, chunking, local embeddings, authorized metadata filtering, semantic retrieval, and citations.

## Phase 5 — MCP

- Expose the specified tools with authorization enforced before data leaves each tool.

## Phase 6 — Agent

- Add model-neutral orchestration, tool selection, evidence, sources, revisions, and lineage-aware answers.

## Phase 7 — RBAC and audit

- Add synthetic roles, backend enforcement, access-denial logging, model/response metadata, and audit queries.

## Phase 8 — React UI

- Build the dashboard, domain pages, assistant, governance, lineage, and audit experiences.

## Phase 9 — Test hardening

- Complete API, MCP contract, authorization, revision, retrieval, data-quality, lineage, and forbidden-access coverage.

## Phase 10 — Docker and CI/CD

- Add local orchestration, CI gates, production builds, container builds, and GitHub Pages deployment.
