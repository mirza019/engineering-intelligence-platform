# Architecture decisions

## Authorization precedes retrieval

API handlers and MCP tools construct a trusted user context and require a resource permission before reading protected collections. Supplier document retrieval applies the external-classification filter before ranking.

## Revision metadata is separate

`engineering_documents` owns document identity. `document_revisions` owns revision state and classification. `document_chunks` references a revision, preventing obsolete chunks from masquerading as current content. A partial unique index permits one current released revision per document.

## Model-neutral generation

The agent depends on `LLMProvider`; `OllamaQwenProvider` is the local implementation. Retrieval, authorization, MCP, evidence, and audit logic do not depend on Ollama.

## Local-first graceful degradation

PostgreSQL/pgvector and Qwen are the intended runtime. Deterministic JSON and lexical scoring provide an offline portfolio/demo fallback without weakening the security boundary or current-revision rules.
