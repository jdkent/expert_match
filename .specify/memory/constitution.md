<!--
Sync Impact Report
Version change: 1.0.0 -> 2.0.0
Modified principles:
- I. AWS-Native Service Boundaries -> I. Containerized Service Boundaries
- V. Testable and Observable Delivery -> V. Testable and Observable Delivery
Added sections:
- None
Removed sections:
- None
Templates requiring updates:
- ✅ updated .specify/templates/plan-template.md
- ✅ updated .specify/templates/spec-template.md
- ✅ updated .specify/templates/tasks-template.md
- ✅ reviewed .specify/templates/agent-file-template.md (no change needed)
- ⚠ pending .specify/templates/commands/ (directory not present in repository)
Follow-up TODOs:
- Re-run /speckit.plan for 001-expert-matching-app so the active implementation plan
  reflects the amended non-Kubernetes deployment rule.
-->
# Expert Match Constitution

## Core Principles

### I. Containerized Service Boundaries
Expert Match MUST be implemented as a three-tier web system: a Vite frontend, a
Python backend, and a PostgreSQL database. Each tier MUST keep a clear ownership
boundary, an independently deployable container image, and a documented interface
contract. Local orchestration MUST use Docker Compose. AWS deployment MUST use the
simplest containerized topology that satisfies the feature's scale, reliability,
backup, and recovery needs; added orchestration complexity such as Kubernetes MUST be
explicitly justified in the implementation plan rather than assumed by default.
Rationale: stable service boundaries matter more than a mandatory orchestrator, and
the project's target scale often favors simpler operations.

### II. Canonical Embedding and Retrieval Pipeline
All semantic retrieval features MUST generate embeddings with SPECTER2 from Hugging
Face and MUST compare vectors with cosine similarity. The codebase MUST define one
canonical pipeline for text preprocessing, embedding generation, normalization,
storage shape, and query-time comparison so results remain reproducible across
environments. Any change to the embedding model, vector normalization, chunking
strategy, or similarity math MUST include fresh benchmarks and an explicit migration
decision before implementation. Rationale: retrieval quality depends on stable,
reproducible math.

### III. Benchmark-Guided Performance for Small-Scale Retrieval
Performance work MUST be justified with benchmarks, not intuition. Any change that
affects embedding generation, vector storage, query execution, caching, or memory
layout MUST record latency and memory measurements for representative datasets in the
10, 100, and 1,000-plus embedding range, plus the query mix used to produce those
numbers. Plans and specs MUST define explicit performance budgets for affected
features, and tasks MUST include benchmark execution when retrieval code changes.
Rationale: the target scale is small enough for simple designs to win unless
measurements prove otherwise.

### IV. Rewrite Over Backward Compatibility
Backward compatibility is not a governing constraint for this project. When a
materially better design is identified, the implementation MUST be rewritten
directly, and obsolete code paths, schemas, and interfaces MUST be removed instead
of preserved behind compatibility layers, unless an active rollout constraint is
explicitly documented in the spec. Each rewrite MUST document the simplification or
measured improvement it delivers. Rationale: the project optimizes for better system
design, not for legacy interface preservation.

### V. Testable and Observable Delivery
Every feature MUST ship with automated tests and operational visibility proportional
to its risk. Backend changes MUST include unit, integration, or contract coverage for
business logic and APIs; retrieval changes MUST include correctness tests against
known similarity expectations and benchmark artifacts; deployment changes MUST
validate Docker Compose startup and the production deployment artifacts selected for
that feature. Production-oriented code MUST emit structured logs and expose basic
health or readiness signals. Rationale: if behavior or operability cannot be
verified locally, it will not be reliable in production.

## Technical Standards

- The frontend MUST be a Vite-based web application with its own dependency and build
  pipeline.
- The backend MUST be implemented in Python and expose typed service interfaces and
  explicit configuration boundaries.
- PostgreSQL MUST be the system of record for application data; any additional data
  store for embeddings or caching MUST be benchmarked and justified in the plan.
- Container images MUST be the deployment unit for every runtime service.
- Each feature that affects retrieval or ranking MUST define benchmark inputs, target
  latency or memory budgets, and the hardware assumptions used to evaluate them.

## Delivery Workflow

- Specifications MUST define user scenarios, functional requirements, non-functional
  requirements, benchmark budgets, and deployment expectations before implementation.
- Implementation plans MUST pass a constitution check covering service boundaries,
  deployment simplicity, embedding pipeline decisions, benchmark scope, rewrite
  scope, and observability.
- Task lists MUST include the container, database, testing, benchmark, and
  deployment work needed for the affected feature.
- Reviews MUST reject performance claims without benchmark evidence and MUST reject
  compatibility-preserving dead code unless a rollout constraint is documented.

## Governance

This constitution supersedes conflicting local conventions. Amendments require an
update to this file, synchronized changes to affected templates or guidance files,
and a recorded semantic-version rationale in the sync impact report. Compliance
review is mandatory for every specification, implementation plan, task list, and code
review; non-compliant work MUST not merge until the implementation is corrected or
the constitution is amended first.

Versioning policy for this constitution:

- MAJOR: Removes or materially redefines a principle or governance rule.
- MINOR: Adds a principle or materially expands a required practice or section.
- PATCH: Clarifies wording without changing enforcement.

This adoption establishes the initial governing baseline for the repository.

**Version**: 2.0.0 | **Ratified**: 2026-03-24 | **Last Amended**: 2026-03-24
