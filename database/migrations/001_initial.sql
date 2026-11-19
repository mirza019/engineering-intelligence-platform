CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE projects (
  project_id text PRIMARY KEY, project_name text NOT NULL, customer text NOT NULL,
  country text NOT NULL, project_manager text NOT NULL, project_status text NOT NULL,
  project_type text NOT NULL, start_date date NOT NULL, planned_completion_date date NOT NULL
);
CREATE TABLE milestones (
  milestone_id text PRIMARY KEY, project_id text NOT NULL REFERENCES projects(project_id),
  milestone_name text NOT NULL, planned_date date NOT NULL, actual_date date, status text NOT NULL
);
CREATE TABLE equipment (
  equipment_id text PRIMARY KEY, project_id text NOT NULL REFERENCES projects(project_id),
  equipment_type text NOT NULL, manufacturer text NOT NULL, specification text NOT NULL, status text NOT NULL
);
CREATE TABLE quality_issues (
  ncc_id text PRIMARY KEY, project_id text NOT NULL REFERENCES projects(project_id),
  equipment_id text NOT NULL REFERENCES equipment(equipment_id), title text NOT NULL, description text NOT NULL,
  severity text NOT NULL, root_cause text NOT NULL, corrective_action text NOT NULL, status text NOT NULL,
  opened_date date NOT NULL, closed_date date, classification text NOT NULL DEFAULT 'internal'
);
CREATE TABLE lessons_learned (
  lesson_id text PRIMARY KEY, project_type text NOT NULL, equipment_type text NOT NULL,
  problem text NOT NULL, root_cause text NOT NULL, impact text NOT NULL, recommendation text NOT NULL,
  source_project text NOT NULL REFERENCES projects(project_id), date date NOT NULL, classification text NOT NULL
);
CREATE TABLE engineering_documents (
  document_id text PRIMARY KEY, project_id text NOT NULL REFERENCES projects(project_id),
  equipment_id text REFERENCES equipment(equipment_id), title text NOT NULL, document_type text NOT NULL
);
CREATE TABLE document_revisions (
  revision_id text PRIMARY KEY, document_id text NOT NULL REFERENCES engineering_documents(document_id),
  revision text NOT NULL, revision_status text NOT NULL, is_current boolean NOT NULL DEFAULT false,
  classification text NOT NULL, created_date date NOT NULL,
  UNIQUE(document_id, revision)
);
CREATE UNIQUE INDEX one_current_released_revision ON document_revisions(document_id)
  WHERE is_current AND revision_status = 'Released';
CREATE TABLE document_chunks (
  chunk_id text PRIMARY KEY, revision_id text NOT NULL REFERENCES document_revisions(revision_id),
  content text NOT NULL, embedding vector(384)
);
CREATE TABLE governance_metadata (
  data_product_name text PRIMARY KEY, business_owner text NOT NULL, data_steward text NOT NULL,
  authoritative_source text NOT NULL, classification text NOT NULL, quality_status text NOT NULL,
  last_updated timestamptz NOT NULL, retention_rule text NOT NULL, allowed_roles jsonb NOT NULL
);
CREATE TABLE quality_test_results (
  result_id bigserial PRIMARY KEY, rule_name text NOT NULL, data_product text NOT NULL,
  passed boolean NOT NULL, checked_at timestamptz NOT NULL DEFAULT now(), details jsonb NOT NULL
);
CREATE TABLE audit_log (
  audit_id bigserial PRIMARY KEY, username text NOT NULL, role text NOT NULL, timestamp timestamptz NOT NULL DEFAULT now(),
  question text, tools_called jsonb NOT NULL DEFAULT '[]', data_products jsonb NOT NULL DEFAULT '[]',
  documents_retrieved jsonb NOT NULL DEFAULT '[]', access_denied boolean NOT NULL DEFAULT false,
  model text, response_id uuid
);
