<!-- Sync Impact Report:
Version change: 2.0.0 → 3.0.0 (major architectural evolution for Phase V cloud-native deployment)
Modified principles:
  - AI Execution Stack Adherence → expanded to include Kafka, Dapr, Kubernetes
  - Statelessness Requirement → enhanced with event-driven patterns
Added sections:
  - Event-Driven Architecture Law
  - Dapr Integration Principles
  - Kubernetes & Cloud-Native Standards
  - Advanced Feature Requirements
  - Observability & Monitoring
  - CI/CD Requirements
Removed sections: None (all Phase III principles retained and extended)
Templates requiring updates:
  - ⚠ .specify/templates/plan-template.md (needs event-driven architecture section)
  - ⚠ .specify/templates/spec-template.md (needs Kafka/Dapr integration requirements)
  - ⚠ .specify/templates/tasks-template.md (needs deployment and observability tasks)
Follow-up TODOs:
  - Update plan template to include Dapr component design
  - Update spec template to include Kafka topic definitions
  - Update tasks template to include Kubernetes manifest creation tasks
-->
# AI Todo Chatbot Constitution
(Phase V — Cloud-Native, Event-Driven, Kubernetes-Deployed System)

## Core Identity

### I. AI Task-Management Assistant Identity
You are a task-management AI assistant operating in a cloud-native, event-driven architecture, powered by OpenAI Agents SDK logic, using Cohere API as the underlying LLM provider, and communicating exclusively through MCP tools. The system is deployed on Kubernetes (Minikube locally, cloud-managed clusters in production), uses Kafka (Redpanda) for event streaming, and leverages Dapr for distributed application runtime capabilities. You are NOT a replacement for backend logic, allowed to manipulate database state directly, allowed to store memory in RAM or session variables, or allowed to invent APIs, tools, or fields not defined in the spec.

### II. Architectural Law (Non-Negotiable)
1. ALL task operations MUST go through MCP tools
2. MCP tools are stateless and persist state only via database
3. The FastAPI server holds ZERO conversational state
4. Conversation context MUST be reconstructed from database per request
5. Every request must be independently reproducible
6. Existing Phase I & II backend logic MUST remain untouched
7. Authentication context comes from Better Auth (user_id / email)
8. ALL task operations MUST publish events to Kafka topics
9. Services MUST communicate through Dapr building blocks (not direct calls)
10. System MUST be deployable on both Minikube and cloud Kubernetes
11. Infrastructure dependencies MUST be abstracted through Dapr components

Violation of any rule is a SYSTEM FAILURE.

## Core Principles

### III. AI Execution Stack Adherence
Adhere strictly to the designated technology stack: OpenAI ChatKit for frontend interface, OpenAI Agents SDK for agent logic, Cohere API for LLM provision, Official MCP SDK for tool layer, Python FastAPI for backend, SQLModel for ORM, Neon Serverless PostgreSQL for database, Kafka (Redpanda Cloud) for event streaming, Dapr for distributed runtime, and Kubernetes for orchestration. Respect the full stack integration with proper authentication flow, database connections, tool execution pathways, event publishing, and service invocation patterns.

### IV. MCP-First Operations (Non-Negotiable)
All task operations must exclusively use MCP tools without exception. Available tools: add_task, list_tasks, complete_task, delete_task, and update_task. Each tool requires proper user_id authentication and follows the specified parameters. Never bypass MCP tools to access database directly. Maintain strict tool usage for all data operations. MCP tools MUST publish events to Kafka after successful operations.

### V. Event-Driven Architecture Law
Every task operation (create, update, complete, delete) MUST publish an event to the appropriate Kafka topic. Use designated topics: `task-events` for lifecycle operations, `reminders` for due date notifications, `task-updates` for real-time synchronization. Events MUST be published through Dapr Pub/Sub component (not direct Kafka clients). Event schemas MUST be consistent and versioned. Consumers MUST be idempotent and handle duplicate events gracefully.

### VI. Dapr Integration Principles
All infrastructure interactions MUST go through Dapr building blocks:
- **Pub/Sub**: Use `kafka-pubsub` component for event streaming (never direct Kafka clients)
- **State Management**: Use `statestore` component for distributed state (PostgreSQL-backed)
- **Service Invocation**: Use Dapr service-to-service calls (not direct HTTP)
- **Cron Bindings**: Use `reminder-cron` for scheduled reminder checks
- **Secrets Management**: Use `secretstores.k8s` for credentials (never hardcode)

Dapr sidecars MUST be deployed alongside every service. Component definitions MUST be environment-specific (local vs cloud).

### VII. Kubernetes & Cloud-Native Standards
System MUST be fully containerized and deployable on Kubernetes. Support both local (Minikube) and cloud platforms (DOKS, GKE, or AKS). Use Kubernetes manifests for all deployments (Deployments, Services, ConfigMaps, Secrets). Implement proper health checks (liveness, readiness probes). Use resource limits and requests. Support horizontal pod autoscaling where appropriate. Maintain environment parity between local and cloud deployments.

### VIII. Statelessness Requirement
Maintain strict stateless operation where the FastAPI server holds zero conversational state. Conversation context must be reconstructed from database per request. Every request must be independently reproducible. Never store memory in RAM or session variables. Authentication context comes from Better Auth (user_id / email). Services MUST be horizontally scalable without session affinity requirements.

### IX. User Context & Security
Always operate with authenticated user context knowing the user_id and email. Never access or describe another user's data. Use user_id explicitly in every MCP tool call. Be privacy-aware and secure. Respect Better Auth user boundaries and ensure data isolation between users. Secrets MUST be managed through Dapr secrets component or Kubernetes secrets. Never log sensitive user data or credentials.

## Advanced Feature Requirements

### X. Recurring Tasks
Support recurring task patterns (daily, weekly, monthly, custom intervals). When a recurring task is completed, publish event to `task-events` topic. Recurring service consumes event and creates next instance based on recurrence rule. Original task metadata (title, description, priority, tags) MUST be preserved. User MUST be able to modify or stop recurrence patterns.

### XI. Due Dates & Reminders
Tasks MUST support optional due dates with timezone awareness. Reminder service uses Dapr cron binding to check for upcoming due dates. When reminder threshold is reached, publish event to `reminders` topic. Notification service consumes reminder events and delivers notifications to users. Support configurable reminder intervals (1 hour, 1 day, 1 week before due date).

### XII. Notifications
Implement notification delivery system consuming from `reminders` topic. Support multiple notification channels (in-app, email, push notifications). Notifications MUST be user-specific and respect user preferences. Track notification delivery status. Implement retry logic for failed deliveries. Never spam users with duplicate notifications.

### XIII. Intermediate Features
Implement the following features with proper event publishing:
- **Priorities**: High, Medium, Low priority levels with filtering and sorting
- **Tags**: User-defined tags for task categorization with multi-tag support
- **Search**: Full-text search across task titles and descriptions
- **Filter**: Filter by status, priority, tags, due date ranges
- **Sort**: Sort by creation date, due date, priority, completion status

All filter/search/sort operations MUST respect user_id boundaries and perform efficiently with proper database indexes.

## Operational Requirements

### XIV. Observability & Monitoring
Implement comprehensive observability across all services:
- **Logging**: Structured JSON logs with correlation IDs, log levels (DEBUG, INFO, WARN, ERROR)
- **Metrics**: Expose Prometheus-compatible metrics (request counts, latencies, error rates)
- **Health Checks**: Implement `/health` and `/ready` endpoints for Kubernetes probes
- **Distributed Tracing**: Use correlation IDs across service boundaries and event flows
- **Alerting**: Define alert thresholds for critical metrics (error rates, latency p95, queue depths)

Logs MUST NOT contain sensitive data. Metrics MUST be aggregatable across pod replicas.

### XV. CI/CD Requirements
Implement automated CI/CD pipeline using GitHub Actions:
- **Build**: Compile, lint, test on every push
- **Docker**: Build and tag container images with commit SHA and semantic versions
- **Registry**: Push images to container registry (Docker Hub, GCR, or ACR)
- **Deploy**: Automatically deploy to Kubernetes on merge to main branch
- **Rollback**: Support automated rollback on deployment failures
- **Environments**: Support dev, staging, production environments with promotion workflow

Pipeline MUST fail on test failures, security vulnerabilities, or linting errors.

## Additional Constraints

### Security Requirements
- All MCP tools must include user_id for proper authentication and authorization
- Database queries must filter by authenticated user_id to prevent data leakage
- Never store sensitive credentials in code; use Dapr secrets or Kubernetes secrets only
- MCP tools must validate user permissions before executing operations
- Never fabricate task data or leak internal IDs unnecessarily
- Kafka events MUST NOT contain sensitive user credentials
- Service-to-service communication MUST use Dapr mTLS
- Container images MUST be scanned for vulnerabilities before deployment

### Performance Standards
- MCP tools should respond within 2 seconds under normal load
- Database queries must use appropriate indexes for user_id filtering
- Conversation history retrieval must be optimized for performance
- Tool execution should be efficient and avoid unnecessary database calls
- State reconstruction from database must be fast and reliable
- Event publishing MUST be asynchronous and non-blocking
- Kafka consumers MUST process events within 5 seconds
- System MUST handle at least 100 concurrent users per pod

### Functional Requirements
- Support natural language processing for task management
- Enable add, list, update, complete, and delete operations
- Handle tool chaining when needed for complex operations
- Provide user-friendly error messages
- Maintain compatibility with existing backend logic
- Support all advanced features (recurring, reminders, notifications)
- Support all intermediate features (priorities, tags, search, filter, sort)
- Maintain real-time synchronization across multiple clients via WebSocket

## Development Workflow

### Implementation Sequence
Follow the strict sequence: sp.constitution → sp.clarify (when ambiguity exists) → sp.plan → sp.tasks → sp.implement. Always reference relevant spec files with @specs/ notation, maintain WHAT/WHY vs HOW separation, clarify ambiguities before proceeding, and verify constitution compliance after each step. Prioritize MCP tool integration, event-driven patterns, Dapr component configuration, and Kubernetes manifest creation.

### Review Process
All code changes must demonstrate constitution compliance with the following checklist:
- [ ] All task operations go through MCP tools?
- [ ] Maintained stateless server architecture?
- [ ] Used proper user_id in all tool calls?
- [ ] Respected Better Auth authentication context?
- [ ] MCP tools are stateless and database-only?
- [ ] Conversation context reconstructed from database?
- [ ] Existing backend logic remains untouched?
- [ ] Events published to appropriate Kafka topics?
- [ ] Used Dapr building blocks (not direct infrastructure calls)?
- [ ] Kubernetes manifests include health checks and resource limits?
- [ ] Secrets managed through Dapr or Kubernetes secrets?
- [ ] Observability implemented (logs, metrics, health endpoints)?
- [ ] CI/CD pipeline configured and tested?

### Quality Gates
- All MCP tools must pass authentication validation
- Database operations must include proper user isolation
- Statelessness requirements must be strictly followed
- Natural language processing must map correctly to tools
- Error handling must be user-friendly and secure
- Tool chaining must work properly for complex operations
- Event publishing must be reliable and asynchronous
- Dapr components must be properly configured for environment
- Kubernetes deployments must pass health checks
- Container images must pass security scans
- CI/CD pipeline must execute successfully
- System must run on both Minikube and cloud Kubernetes

## Governance

This constitution represents immutable, non-negotiable principles that every agent, skill, spec, plan, task, and code generation must follow. All implementation work must self-check against this constitution before finalizing any output. Amendments require explicit user approval and must be documented with clear rationale. The constitution supersedes all other development practices and serves as the ultimate authority for code quality and architectural decisions.

The primary objective is to enable users to manage their todos via natural language while maintaining system integrity, scalability, and cloud-native operational excellence. The chatbot must be able to add, list, update, complete, delete tasks, explain user identity, resume conversations after server restarts, and support advanced features (recurring tasks, reminders, notifications) and intermediate features (priorities, tags, search, filter, sort). All operations must follow the natural language to tool mapping rules, maintain stateless operation, publish events to Kafka, use Dapr building blocks, and be deployable on Kubernetes.

### Amendment Process
1. Proposed changes must be submitted with clear rationale and impact analysis
2. Major version bumps require architectural review and user approval
3. Minor version bumps require documentation of new principles or expanded guidance
4. Patch version bumps for clarifications and non-semantic changes
5. All amendments must update the Sync Impact Report
6. Dependent templates and documentation must be updated within same change

### Compliance Review
- Constitution compliance must be verified at each development stage
- Automated checks should enforce non-negotiable principles where possible
- Manual review required for architectural decisions and new feature additions
- Violations must be documented and remediated before proceeding

**Version**: 3.0.0 | **Ratified**: 2026-02-02 | **Last Amended**: 2026-02-09
