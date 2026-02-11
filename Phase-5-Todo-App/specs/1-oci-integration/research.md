# Research Document: OCI Full System Integration & Deployment

**Feature**: 1-oci-integration
**Created**: 2026-02-09

## R0.1: Oracle Cloud Infrastructure Research

### Decision: OCI Streaming Service vs Managed Kafka
**Rationale**: OCI Streaming Service is Oracle's native Kafka-compatible service that integrates well with other OCI services. It offers managed Kafka functionality without requiring separate Kafka cluster management.

**Alternatives considered**:
- Self-hosted Kafka cluster on OCI VMs (higher operational overhead)
- Third-party Kafka managed service (potential vendor lock-in concerns)
- OCI Streaming Service (recommended - native integration)

### Decision: OKE Cluster Configuration
**Rationale**: Using OKE ensures tight integration with OCI ecosystem. Recommended configuration includes at least 3 nodes for high availability with auto-scaling enabled.

**Alternatives considered**:
- Single node cluster (not production-ready)
- 3-node cluster with auto-scaling (recommended - HA + cost-effective)
- Larger fixed-size cluster (higher cost)

### Decision: OCI Container Registry Strategy
**Rationale**: OCIR provides native integration with OKE and built-in security scanning capabilities.

**Alternatives considered**:
- Docker Hub (external dependency)
- OCIR (recommended - native OCI integration)
- Harbor registry on OCI (self-managed complexity)

## R0.2: Dapr Component Configuration Research

### Decision: Kafka PubSub Component Configuration
**Rationale**: Using Dapr's Kafka component allows abstracting the underlying event system while maintaining flexibility.

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "{{.kafkaEndpoint}}"
  - name: authRequired
    value: "true"
  - name: consumerGroup
    value: "dapr-consumer-group"
  - name: clientID
    value: "dapr-kafka-client"
```

**Alternatives considered**:
- Direct Kafka client usage (violates constitution)
- Dapr Kafka component (recommended - compliant)
- Other pubsub components (may not support Kafka features)

### Decision: PostgreSQL State Store Component
**Rationale**: Using PostgreSQL as the state store maintains consistency with existing database while leveraging Dapr's state management features.

**Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: postgresql-statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "postgresql://username:password@host:port/database"
  - name: actorStateStore
    value: "true"
```

### Decision: OCI Vault Secret Store Integration
**Rationale**: Dapr's secret store component can integrate with OCI Vault for secure secret management.

**Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: oci-vault-secrets
spec:
  type: secretstores.hashicorp.vault
  version: v1
  metadata:
  - name: vaultAddr
    value: "https://vault.oci.service"
  - name: skipVerify
    value: "false"
  - name: kvVers
    value: "2"
```

## R0.3: Event-Driven Architecture Patterns

### Decision: Event Schema Design for Task Operations
**Rationale**: Events should follow a consistent schema that includes correlation IDs and follows CloudEvents specification where possible.

**Schema for task-events**:
```json
{
  "eventId": "unique-event-id",
  "source": "/services/backend",
  "type": "task.created",
  "subject": "task:123",
  "time": "2026-02-09T10:00:00Z",
  "data": {
    "taskId": "123",
    "userId": "user456",
    "operation": "create",
    "taskData": {...},
    "timestamp": "2026-02-09T10:00:00Z"
  }
}
```

### Decision: Event Topic Strategy
**Rationale**: Three topics provide clear separation of concerns:
- `task-events`: For all task lifecycle operations
- `reminders`: For due date and notification events
- `task-updates`: For real-time synchronization events

### Decision: Consumer Group Strategy
**Rationale**: Using consumer groups allows for scalable event processing with proper load distribution.

## R0.4: Security and Compliance Validation

### Decision: Dapr Security Model
**Rationale**: Dapr provides built-in mTLS between services, which satisfies the constitution's requirement for secure service-to-service communication.

### Decision: Network Security
**Rationale**: Using Kubernetes Network Policies to isolate service communication and only exposing necessary ports through Ingress.

### Decision: Secret Management Approach
**Rationale**: Combining OCI Vault with Dapr's secret store abstraction provides secure secret management while maintaining code security (no hardcoded secrets).

**Validation**: All approaches comply with constitution requirements:
- No direct infrastructure access (all through Dapr)
- Secrets managed externally (OCI Vault)
- mTLS enabled for service communication
- No hardcoded credentials in code