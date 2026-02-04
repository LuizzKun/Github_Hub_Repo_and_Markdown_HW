# Technology Decision Records — Campus Event Hub

---

## TDR 001 — Programming Language: Python

**Status:** Accepted

### Context
Campus Event Hub is developed by a small team and is intended as an internal
university system. The technology stack should be easy to learn, maintain,
and suitable for rapid development.

### Decision
Use **Python** as the primary programming language for the backend and application logic.

### Alternatives Considered
- JavaScript (Node.js)
- Java

### Consequences

**Positive:**
- Readable and beginner-friendly language
- Large ecosystem of libraries and frameworks
- Well-suited for rapid development and prototyping

**Negative:**
- Slightly lower raw performance compared to some compiled languages
- Requires careful dependency management in larger projects

---

## TDR 002 — Web Framework / UI Layer: Streamlit

**Status:** Accepted

### Context
The system is an internal web application focused on functionality rather than
complex user interface design. The team has limited frontend development resources.

### Decision
Use **Streamlit** as the primary framework for building the web interface.

### Alternatives Considered
- Django templates
- React or other frontend frameworks

### Consequences

**Positive:**
- Rapid development of forms, tables, and dashboards
- Minimal frontend code required
- Simplifies deployment by combining UI and backend

**Negative:**
- Less control over custom UI design
- Not ideal for highly interactive or public-facing applications

---

## TDR 003 — Data Access Layer: SQLAlchemy

**Status:** Accepted

### Context
The system requires structured data storage and safe database access while
supporting multiple database backends during development and production.

### Decision
Use **SQLAlchemy** as the Object-Relational Mapper (ORM) for database access.

### Alternatives Considered
- Raw SQL queries
- Django ORM

### Consequences

**Positive:**
- Clean abstraction over SQL databases
- Reduces boilerplate code
- Easier database migration between SQLite and PostgreSQL

**Negative:**
- Adds an abstraction layer that may hide SQL details
- Learning curve for advanced queries

---

## TDR 004 — Production Database: PostgreSQL

**Status:** Accepted

### Context
The production system requires reliable data storage, transactional integrity,
and efficient querying for event browsing and filtering.

### Decision
Use **PostgreSQL** as the primary production database.

### Alternatives Considered
- MySQL
- NoSQL databases

### Consequences

**Positive:**
- Strong ACID compliance and reliability
- Excellent performance for relational data
- Widely supported by cloud hosting providers

**Negative:**
- Requires database server setup and management
- Slightly higher operational overhead than file-based databases

---

## TDR 005 — Development Database: SQLite

**Status:** Accepted

### Context
Early development and testing should be as simple as possible, without requiring
a full database server setup.

### Decision
Use **SQLite** as the database during early development and local testing.

### Alternatives Considered
- PostgreSQL for all environments

### Consequences

**Positive:**
- Zero setup and easy local development
- Fast prototyping and testing
- Seamless transition to PostgreSQL using SQLAlchemy

**Negative:**
- Not suitable for high concurrency
- Not intended for long-term production use

---

## TDR 006 — Deployment Platform

**Status:** Accepted

### Context
The system must be easy to deploy and maintain with limited operational resources.

### Decision
Deploy the system as a **single Streamlit application** with a **managed PostgreSQL**
database in production.

### Alternatives Considered
- Kubernetes-based deployment
- Multiple independent services

### Consequences

**Positive:**
- Simple deployment and maintenance
- Low operational overhead
- Matches monolithic architecture decisions

**Negative:**
- Limited scalability compared to complex orchestration platforms
- All features are deployed together

---
