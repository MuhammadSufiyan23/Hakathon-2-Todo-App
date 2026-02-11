---
id: 003
title: Phase V Cloud Native Constitution Update
stage: constitution
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5
feature: none
branch: master
user: system
command: /sp.constitution
labels: ["phase-v", "cloud-native", "kubernetes", "kafka", "dapr", "event-driven"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - .specify/templates/plan-template.md
  - .specify/templates/spec-template.md
  - .specify/templates/tasks-template.md
tests:
  - null
---

## Prompt

# Phase V – Advanced Cloud Deployment (Constitution Prompt)

## Objective
Design and implement a **production-grade, event-driven Todo Chatbot system** and deploy it first on **Minikube (local Kubernetes)** and then on a **cloud-managed Kubernetes platform** such as **DigitalOcean Kubernetes (DOKS)**, **Google Kubernetes Engine (GKE)**, or **Azure Kubernetes Service (AKS)**.

The system must demonstrate **advanced cloud-native architecture** using:
- **Kafka (Redpanda Cloud)** for event streaming
- **Dapr** for distributed application runtime
- **CI/CD pipelines** for automated delivery
- **Monitoring & logging** for observability

---

## Core Requirements

### Part A – Advanced Features
Implement all of the following features in the Todo system:

1. **Advanced Functionality**
   - Recurring Tasks
   - Due Dates & Reminders
   - Notifications

2. **Intermediate Functionality**
   - Priorities
   - Tags
   - Search
   - Filter
   - Sort

3. **Event-Driven Architecture**
   - All task operations must publish events to Kafka.
   - Use topics:
     - `task-events`
     - `reminders`
     - `task-updates`

4. **Dapr Integration**
   Use Dapr building blocks:
   - Pub/Sub (Kafka abstraction)
   - State Management
   - Service Invocation
   - Cron Bindings
   - Secrets Management

---

## Part B – Local Deployment (Minikube)

### Goals
Deploy the full system locally using Kubernetes and Dapr.

### Requirements
- Deploy all services on **Minikube**
- Install Dapr on Minikube
- Use full Dapr features:
  - Pub/Sub (Kafka)
  - State Store
  - Cron Bindings
  - Secrets
  - Service Invocation

---

## Part C – Cloud Deployment

### Cloud Platforms (choose one)
- DigitalOcean Kubernetes (DOKS)
- Google Kubernetes Engine (GKE)
- Azure Kubernetes Service (AKS)

### Cloud Requirements
- Deploy the same system on cloud Kubernetes
- Use **Redpanda Cloud (Serverless Kafka)**
- Deploy **Dapr on cloud cluster**

---

## Event-Driven Use Cases

### 1. Reminder System
When a task has a due date:
Todo Service → Kafka (reminders) → Notification Service → User

### 2. Recurring Task Engine
When a task is completed:
Todo Service → Kafka (task-events) → Recurring Service → New Task

### 3. Audit Log
Every operation:
All Services → Kafka (task-events) → Audit Service

### 4. Real-Time Sync
Task changes:
Todo Service → Kafka (task-updates) → WebSocket → All Clients

---

## Kafka Topics

| Topic         | Producer      | Consumer                     | Purpose |
|--------------|--------------|------------------------------|--------|
| task-events  | Backend API  | Recurring, Audit Services    | Task lifecycle |
| reminders    | Backend API  | Notification Service         | Reminders |
| task-updates | Backend API  | WebSocket Service            | Live sync |

---

## Dapr Components

| Component | Type | Purpose |
|----------|------|--------|
| kafka-pubsub | pubsub.kafka | Event streaming |
| statestore | state.postgresql | State storage |
| reminder-cron | bindings.cron | Scheduled jobs |
| secrets | secretstores.k8s | Secure credentials |

---

## CI/CD Requirements
Set up **GitHub Actions** pipeline:
- Build Docker images
- Push to registry
- Deploy to Kubernetes automatically

---

## Observability
Implement:
- Logging (application + Kubernetes)
- Metrics (Prometheus or equivalent)
- Health checks

---

## Final Deliverables

1. Public GitHub Repository:
   - All source code
   - `/specs` folder
   - Kubernetes manifests
   - Dapr components
   - CI/CD workflows

2. Deployed URLs:
   - Local Minikube demo
   - Cloud deployment URL

3. Demo Video (max 90s):
   - Show features
   - Show Kafka flow
   - Show Dapr in action

---

## Success Criteria
This phase is considered complete when:
- The system runs locally on Minikube
- The same system runs on cloud Kubernetes
- All services communicate via Kafka
- Dapr is used instead of direct infrastructure calls
- CI/CD automatically deploys changes
- Architecture is scalable, decoupled, and observable

## Response snapshot

Updated project constitution from version 2.0.0 to 3.0.0 with major architectural evolution for Phase V cloud-native deployment.

**Key Changes:**
- Added 4 new architectural laws (rules 8-11) for event-driven and Kubernetes requirements
- Expanded AI Execution Stack to include Kafka (Redpanda), Dapr, and Kubernetes
- Added 6 new principle sections: Event-Driven Architecture Law, Dapr Integration Principles, Kubernetes & Cloud-Native Standards, Advanced Feature Requirements (Recurring Tasks, Due Dates & Reminders, Notifications), Intermediate Features (Priorities, Tags, Search, Filter, Sort), Observability & Monitoring, CI/CD Requirements
- Enhanced review checklist with 6 new compliance checks for events, Dapr, Kubernetes, secrets, observability, and CI/CD
- Updated all templates (plan, spec, tasks) to include Phase V sections for event-driven architecture, Dapr components, Kubernetes deployment, and observability

**Template Updates:**
- plan-template.md: Added Event-Driven Architecture, Dapr Components, and Kubernetes Deployment sections
- spec-template.md: Added Event-Driven Requirements and Cloud-Native Requirements sections
- tasks-template.md: Added Event-Driven Integration, Kubernetes & Cloud Deployment, and Observability & CI/CD phases

**Version Rationale:**
Major version bump (2.0.0 → 3.0.0) due to fundamental architectural changes introducing event-driven patterns, distributed runtime requirements, and cloud-native deployment standards that significantly alter system design and implementation approach.

## Outcome

- ✅ Impact: Constitution updated to v3.0.0 with comprehensive Phase V cloud-native requirements. All dependent templates updated with new sections for event-driven architecture, Dapr integration, Kubernetes deployment, and observability.
- 🧪 Tests: No automated tests - constitution is a governance document
- 📁 Files: Modified 4 files - constitution.md (major update), plan-template.md (added 3 sections), spec-template.md (added 2 sections), tasks-template.md (added 3 phases)
- 🔁 Next prompts: Run /sp.specify or /sp.plan to create feature specifications following new Phase V requirements. Consider running /sp.adr to document architectural decisions for Kafka topic design, Dapr component selection, and Kubernetes deployment strategy.
- 🧠 Reflection: This is a significant architectural evolution that transforms the system from a simple stateless chatbot to a production-grade, event-driven, cloud-native application. The constitution now enforces strict requirements for event publishing, Dapr usage, Kubernetes deployment, observability, and CI/CD that will guide all future development.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution update completed successfully with all templates synchronized
- Graders run and results (PASS/FAIL): Manual validation PASS - all placeholders filled, version incremented correctly, templates updated consistently
- Prompt variant (if applicable): Standard /sp.constitution workflow
- Next experiment (smallest change to try): Test the updated templates by running /sp.specify for a new Phase V feature to validate that the new sections provide sufficient guidance for event-driven and cloud-native implementation
