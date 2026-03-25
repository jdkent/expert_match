# Tasks: Expert Matching and Outreach

**Input**: Design documents from `/specs/001-expert-matching-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Automated tests are REQUIRED for every affected flow. Include the
contract, integration, unit, or end-to-end coverage needed to verify the
environment-parity and deployment changes.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. `[US1]`, `[US2]`, `[US3]`)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/`, `frontend/`, `deploy/aws/`, repository-root Compose files
- Paths below assume the structure defined in `plan.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Introduce the new environment-shape files and shared runtime targets

- [X] T001 Create a shared Compose base with local PostgreSQL volume support in `/home/jdkent/projects/match_experts/expert_match/docker-compose.yml`
- [X] T002 [P] Add a development override for Vite hot reload and local-only conveniences in `/home/jdkent/projects/match_experts/expert_match/docker-compose.dev.yml`
- [X] T003 [P] Add a test override for containerized validation workflows in `/home/jdkent/projects/match_experts/expert_match/docker-compose.test.yml`
- [X] T004 [P] Convert the frontend container to multi-stage dev and production targets in `frontend/Dockerfile`
- [X] T005 [P] Add a production Nginx ingress configuration in `deploy/aws/compose/nginx.conf`
- [X] T006 [P] Add shared environment examples for local and AWS deployment in `/home/jdkent/projects/match_experts/expert_match/.env.example` and `deploy/aws/compose/.env.example`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Align configuration, routing, and deployment primitives before story validation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Configure backend DSN-based database and shared environment parsing in `backend/app/core/config.py` and `backend/app/db/session.py`
- [X] T008 [P] Align backend startup and health checks with local PostgreSQL and managed PostgreSQL expectations in `backend/app/main.py` and `backend/app/api/health.py`
- [X] T009 [P] Align frontend API bootstrap with environment-parity `/api` routing in `frontend/src/services/api.ts`, `frontend/package.json`, and `frontend/vite.config.ts`
- [X] T010 [P] Rework the AWS production Compose stack around internal-only backend networking and Nginx ingress in `deploy/aws/compose/docker-compose.prod.yml`
- [X] T011 [P] Update EC2 bootstrap assumptions for Nginx plus external RDS connectivity in `deploy/aws/ec2/cloud-init.sh`
- [X] T012 [P] Add base-plus-override environment strategy notes to agent guidance in `AGENTS.md`

**Checkpoint**: Foundation ready - story-specific parity work can now proceed

---

## Phase 3: User Story 1 - Publish and Edit Expert Profile Through a Parity-Safe Stack (Priority: P1) 🎯 MVP

**Goal**: Keep expert submission, verification, recovery, edit, and deletion working through the same service names and `/api` contract in dev, test, and production

**Independent Test**: Bring up the dev stack with local PostgreSQL, submit and verify a profile through the frontend, recover the edit link, update the profile, and confirm the same API paths remain valid behind the production Nginx ingress shape

### Tests for User Story 1 (REQUIRED) ⚠️

- [X] T013 [P] [US1] Update backend integration coverage for the profile lifecycle against the PostgreSQL-backed container stack in `backend/tests/integration/test_expert_profile_flow.py`
- [X] T014 [P] [US1] Update frontend end-to-end coverage for expert submission and recovery through ingress-relative paths in `frontend/tests/e2e/expert_profile_flow.spec.ts`

### Implementation for User Story 1

- [X] T015 [P] [US1] Align expert profile frontend API calls with the shared `/api` contract in `frontend/src/services/expertProfiles.ts`
- [X] T016 [P] [US1] Update expert profile and recovery UI assumptions for dev/prod parity in `frontend/src/features/expert-profile/ExpertProfileForm.tsx`, `frontend/src/features/expert-profile/ExpertEditRecoveryForm.tsx`, and `frontend/src/pages/ExpertProfilePage.tsx`
- [X] T017 [US1] Ensure expert profile routes and generated verification or edit links respect the shared environment contract in `backend/app/api/expert_profiles.py` and `backend/app/services/expert_profile_service.py`
- [X] T018 [US1] Add compose-backed profile-flow validation steps to `specs/001-expert-matching-app/quickstart.md`

**Checkpoint**: At this point, User Story 1 should be fully functional through the new environment-parity stack

---

## Phase 4: User Story 2 - Find and Contact Experts Through the Same Ingress Contract (Priority: P2)

**Goal**: Keep matching and outreach behavior stable while moving all requester traffic behind the shared ingress and environment contract

**Independent Test**: Run the requester flow through the dev stack, receive distinct expert matches, select a primary expert, and send outreach while using the same `/api` paths and internal service wiring expected in production

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T019 [P] [US2] Update backend integration coverage for matching and outreach under the parity-focused stack in `backend/tests/integration/test_matching_and_outreach_flow.py`
- [X] T020 [P] [US2] Update frontend end-to-end coverage for requester search and outreach through ingress-relative routing in `frontend/tests/e2e/requester_matching_flow.spec.ts`

### Implementation for User Story 2

- [X] T021 [P] [US2] Align requester matching and outreach API clients with the shared ingress contract in `frontend/src/services/matching.ts` and `frontend/src/services/outreach.ts`
- [X] T022 [P] [US2] Update requester search and outreach UI assumptions for the new ingress and environment strategy in `frontend/src/features/matching/MatchQueryForm.tsx`, `frontend/src/features/matching/MatchedExpertList.tsx`, `frontend/src/features/outreach/OutreachComposer.tsx`, and `frontend/src/pages/RequesterSearchPage.tsx`
- [X] T023 [US2] Preserve backend matching and outreach behavior behind reverse-proxy routing and internal container networking in `backend/app/api/matching.py`, `backend/app/api/outreach.py`, `backend/app/services/matching_service.py`, and `backend/app/services/outreach_service.py`

**Checkpoint**: At this point, User Stories 1 and 2 should both work through the same dev/test/prod request model

---

## Phase 5: User Story 3 - Keep Slot Demand Tracking Compatible Across Environments (Priority: P3)

**Goal**: Preserve availability reads and slot-demand counting while the stack moves to shared ingress and PostgreSQL-backed local orchestration

**Independent Test**: Use the parity-focused stack to send repeated outreach requests for the same expert and slots and confirm attendee counts still increase while the same `/api` paths and UI behavior work in both dev and production-style setups

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T024 [P] [US3] Update backend integration coverage for slot counting under the PostgreSQL-backed container stack in `backend/tests/integration/test_slot_counting.py`
- [X] T025 [P] [US3] Update frontend end-to-end coverage for availability selection through the shared ingress contract in `frontend/tests/e2e/availability_selection.spec.ts`

### Implementation for User Story 3

- [X] T026 [P] [US3] Align availability API behavior with the shared environment contract in `backend/app/api/availability.py` and `backend/app/services/availability_service.py`
- [X] T027 [P] [US3] Update availability UI and slot-count rendering to remain ingress-agnostic in `frontend/src/features/availability/AvailabilityGrid.tsx`, `frontend/src/features/availability/SlotCountBadge.tsx`, and `frontend/src/features/outreach/OutreachComposer.tsx`
- [X] T028 [US3] Add parity-focused slot-demand validation steps to `specs/001-expert-matching-app/quickstart.md`

**Checkpoint**: All user stories should now be functional through the updated environment model

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize environment parity, deployment validation, and operator guidance

- [X] T029 [P] Add frontend unit coverage for environment-parity-sensitive API behavior in `frontend/tests/unit/expert-profile.spec.tsx`, `frontend/tests/unit/matched-expert-list.spec.tsx`, and `frontend/tests/unit/outreach-composer.spec.tsx`
- [X] T030 [P] Add backend unit coverage for configuration and database-environment behavior in `backend/tests/unit/test_expert_profile_service.py`, `backend/tests/unit/test_matching_service.py`, `backend/tests/unit/test_outreach_service.py`, and `backend/tests/unit/test_availability_service.py`
- [X] T031 Validate shared Compose definitions for base, dev, test, and production in `/home/jdkent/projects/match_experts/expert_match/docker-compose.yml`, `/home/jdkent/projects/match_experts/expert_match/docker-compose.dev.yml`, `/home/jdkent/projects/match_experts/expert_match/docker-compose.test.yml`, and `deploy/aws/compose/docker-compose.prod.yml`
- [X] T032 Validate frontend dev and production image targets in `frontend/Dockerfile` and `deploy/aws/compose/nginx.conf`
- [X] T033 Validate AWS deployment notes for Nginx ingress, internal-only backend exposure, and RDS connectivity in `deploy/aws/ec2/cloud-init.sh`, `deploy/aws/compose/docker-compose.prod.yml`, and `README.md`
- [X] T034 Validate managed PostgreSQL backup and restore guidance against the updated environment strategy in `deploy/aws/restore-validation.md`
- [X] T035 [P] Finalize operator-facing environment-matrix documentation in `specs/001-expert-matching-app/quickstart.md`, `README.md`, and `AGENTS.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - no dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational but depends on the shared ingress and API contract already being stable from US1 work
- **User Story 3 (P3)**: Can start after Foundational and integrates most cleanly after US2 requester flow changes are in place

### Within Each User Story

- Tests MUST be written and fail before implementation
- Routing and API-client alignment before UI polish
- Backend behavior before deployment validation
- Story complete before moving to the next dependent story

### Parallel Opportunities

- T002-T006 can run in parallel during setup
- T008-T012 can run in parallel once T007 defines the shared environment contract
- US1 test tasks T013-T014 can run in parallel
- US2 test tasks T019-T020 can run in parallel
- US3 test tasks T024-T025 can run in parallel
- Frontend and backend alignment tasks within a story can run in parallel once contracts are stable

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Update backend integration coverage for the profile lifecycle against the PostgreSQL-backed container stack in backend/tests/integration/test_expert_profile_flow.py"
Task: "Update frontend end-to-end coverage for expert submission and recovery through ingress-relative paths in frontend/tests/e2e/expert_profile_flow.spec.ts"

# Launch core US1 alignment work together:
Task: "Align expert profile frontend API calls with the shared /api contract in frontend/src/services/expertProfiles.ts"
Task: "Update expert profile and recovery UI assumptions for dev/prod parity in frontend/src/features/expert-profile/ExpertProfileForm.tsx, frontend/src/features/expert-profile/ExpertEditRecoveryForm.tsx, and frontend/src/pages/ExpertProfilePage.tsx"
```

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
Task: "Update backend integration coverage for matching and outreach under the parity-focused stack in backend/tests/integration/test_matching_and_outreach_flow.py"
Task: "Update frontend end-to-end coverage for requester search and outreach through ingress-relative routing in frontend/tests/e2e/requester_matching_flow.spec.ts"

# Launch core US2 alignment work together:
Task: "Align requester matching and outreach API clients with the shared ingress contract in frontend/src/services/matching.ts and frontend/src/services/outreach.ts"
Task: "Update requester search and outreach UI assumptions for the new ingress and environment strategy in frontend/src/features/matching/MatchQueryForm.tsx, frontend/src/features/matching/MatchedExpertList.tsx, frontend/src/features/outreach/OutreachComposer.tsx, and frontend/src/pages/RequesterSearchPage.tsx"
```

---

## Parallel Example: User Story 3

```bash
# Launch all tests for User Story 3 together:
Task: "Update backend integration coverage for slot counting under the PostgreSQL-backed container stack in backend/tests/integration/test_slot_counting.py"
Task: "Update frontend end-to-end coverage for availability selection through the shared ingress contract in frontend/tests/e2e/availability_selection.spec.ts"

# Launch core US3 alignment work together:
Task: "Align availability API behavior with the shared environment contract in backend/app/api/availability.py and backend/app/services/availability_service.py"
Task: "Update availability UI and slot-count rendering to remain ingress-agnostic in frontend/src/features/availability/AvailabilityGrid.tsx, frontend/src/features/availability/SlotCountBadge.tsx, and frontend/src/features/outreach/OutreachComposer.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run T013-T014 and confirm the expert lifecycle works through the new parity-focused stack
5. Demo the accountless expert submission, verification, recovery, and deletion flow through the shared ingress contract

### Incremental Delivery

1. Complete Setup + Foundational
2. Add User Story 1 → Validate independently → Demo
3. Add User Story 2 → Validate independently → Demo
4. Add User Story 3 → Validate independently → Demo
5. Finish with Compose validation, deployment hardening, and restore validation

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 profile flow parity
   - Developer B: User Story 2 matching/outreach parity
   - Developer C: User Story 3 availability parity and slot-count validation
3. Integrate at story checkpoints before entering Phase 6
