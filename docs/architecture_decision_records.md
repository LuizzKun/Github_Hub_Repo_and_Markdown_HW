# Architecture Decision Records — Campus Event Hub

---

## ADR 001 — Client–Server Architecture

**Status:** Accepted

### Context
Campus Event Hub is an internal university web system where students browse events,
student organizations submit events, and staff administrators review submissions.
The system has low to moderate concurrency and no real-time requirements.

### Decision
Use a **Client–Server architecture**, where users interact through a web interface
(client) and the backend server handles requests, validation, and data storage.

### Alternatives Considered
- Event-Driven Architecture

### Consequences

**Positive:**
- Simple and well-understood communication model
- Immediate feedback for user actions
- Easier to develop and maintain with a small team

**Negative:**
- Less flexible for future real-time or highly distributed use cases
- Tight coupling between client requests and server responses

---

## ADR 002 — Monolithic Deployment

**Status:** Accepted

### Context
The system is developed and maintained by a small team (2–4 engineers) with limited
operational resources. The application’s scope is moderate and primarily CRUD-based.

### Decision
Use a **monolithic architecture**, deploying the backend as a single application.

### Alternatives Considered
- Microservices Architecture

### Consequences

**Positive:**
- Simple deployment and debugging
- Faster development and iteration
- Lower operational and infrastructure overhead

**Negative:**
- Less scalable than microservices at very large scale
- All features must be deployed together

---

## ADR 003 — Feature-Based Code Organization

**Status:** Accepted

### Context
Maintainability is a core requirement. The system must support adding new features
in future semesters without major refactoring or breaking existing functionality.

### Decision
Organize the codebase using a **Feature-Based architecture**, where each feature
(e.g., event submission, event browsing, event review) has its own section of code.

### Alternatives Considered
- Layered Architecture (presentation, business logic, data access)

### Consequences

**Positive:**
- Clear separation between features
- Easier to modify or add features independently
- Reduces unintended side effects between unrelated features

**Negative:**
- Requires discipline to avoid code duplication
- Slightly less familiar than layered architecture for some developers

---

## ADR 004 — Single Shared Database

**Status:** Accepted

### Context
Event data must be consistently accessible across submission, review, and discovery.
The system uses a monolithic backend and does not require independent data ownership.

### Decision
Use a **single shared relational database** for all system data.

### Alternatives Considered
- Database per Service

### Consequences

**Positive:**
- Simple data management and querying
- Immediate consistency for event status updates
- Lower operational overhead

**Negative:**
- All features depend on the same database
- Database schema changes must be coordinated carefully

---

## ADR 005 — Synchronous Interaction Model

**Status:** Accepted

### Context
Users expect immediate responses when submitting events, browsing listings, and
approving or rejecting events.

### Decision
Use **synchronous request/response interactions** for core system functionality.

### Alternatives Considered
- Asynchronous Interaction Model

### Consequences

**Positive:**
- Matches user expectations
- Easier to implement and debug
- Meets acceptance criteria for fast response times

**Negative:**
- Long-running tasks could block responses
- Less suitable for background processing (if added later)

---
