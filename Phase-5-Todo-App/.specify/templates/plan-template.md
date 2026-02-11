# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [single/web/mobile - determines source structure]
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Event-Driven Architecture (Phase V)

<!--
  ACTION REQUIRED: Define event-driven patterns if feature requires event publishing/consumption.
  Remove this section if feature does not involve events.
-->

### Kafka Topics

| Topic Name | Producer Service | Consumer Service(s) | Event Schema | Purpose |
|------------|-----------------|---------------------|--------------|---------|
| [e.g., task-events] | [e.g., Backend API] | [e.g., Recurring Service, Audit Service] | [link to schema or describe] | [e.g., Task lifecycle events] |
| [e.g., reminders] | [e.g., Backend API] | [e.g., Notification Service] | [link to schema or describe] | [e.g., Due date reminders] |

### Event Flow Diagrams

```text
[Describe key event flows, e.g.:]

User Action → Backend API → Kafka (task-events) → Recurring Service → New Task Created
                          ↓
                    Database Update
```

### Event Schemas

**Event: [EventName]**
```json
{
  "event_type": "string",
  "user_id": "string",
  "task_id": "string",
  "timestamp": "ISO8601",
  "payload": { }
}
```

## Dapr Components (Phase V)

<!--
  ACTION REQUIRED: Define Dapr component configurations if feature uses Dapr.
  Remove this section if feature does not use Dapr.
-->

### Required Dapr Components

| Component Name | Type | Purpose | Configuration Notes |
|---------------|------|---------|---------------------|
| kafka-pubsub | pubsub.kafka | Event streaming | Redpanda Cloud (production), local Redpanda (dev) |
| statestore | state.postgresql | Distributed state | PostgreSQL-backed state management |
| reminder-cron | bindings.cron | Scheduled jobs | Cron expression for reminder checks |
| secrets | secretstores.kubernetes | Secret management | K8s secrets for credentials |

### Service-to-Service Communication

- Services MUST use Dapr service invocation (not direct HTTP)
- Example: `http://localhost:3500/v1.0/invoke/[service-name]/method/[endpoint]`

## Kubernetes Deployment (Phase V)

<!--
  ACTION REQUIRED: Define Kubernetes deployment strategy if feature requires K8s deployment.
  Remove this section if feature does not deploy to Kubernetes.
-->

### Deployment Targets

- **Local**: Minikube with Dapr installed
- **Cloud**: [DOKS / GKE / AKS - specify which platform]

### Resource Requirements

| Service | CPU Request | CPU Limit | Memory Request | Memory Limit | Replicas |
|---------|-------------|-----------|----------------|--------------|----------|
| [service-name] | [e.g., 100m] | [e.g., 500m] | [e.g., 128Mi] | [e.g., 512Mi] | [e.g., 2] |

### Health Checks

- **Liveness Probe**: `GET /health` (checks if service is alive)
- **Readiness Probe**: `GET /ready` (checks if service can accept traffic)

### ConfigMaps & Secrets

- **ConfigMaps**: [list environment-specific configs]
- **Secrets**: [list secrets needed - managed via Dapr secrets component]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
