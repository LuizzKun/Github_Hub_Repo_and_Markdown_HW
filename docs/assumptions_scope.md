# Campus Event Hub — Assumptions & Scope

## Project Overview
Campus Event Hub is an internal university web application that centralizes
event submission, review, and discovery for students and staff.

---

## Assumptions
- This is an **internal university system**, not a public commercial product.
- Expected users:
  - Hundreds of students browsing and searching events
  - Dozens of student organization leaders submitting events
  - A small number of staff administrators reviewing events
- Concurrent usage is **low to moderate**.
- No strict real-time or high-availability requirements.
- The system is built and maintained by a **small team (2–4 engineers)**.
- Cloud hosting is available, but **budget and operational resources are limited**.
- Most system functionality is **CRUD-based**.

---

## In Scope
- Event submission:
  - Title, date, time, location, and description
  - Input validation and error messages
  - Events saved with status **submitted**
  - Confirmation message on successful submission
- Event discovery:
  - Browse and search approved upcoming events
  - Filter by date or category
  - View event details
- Event review:
  - Admins can approve or reject submitted events
  - Approved events are visible to students
  - Rejected events are not visible
- Maintainability:
  - New features can be added with minimal refactoring
  - Changes to one feature should not impact unrelated features

---

## Out of Scope
- Native mobile applications
- Public APIs for external partners
- Real-time chat or streaming
- Advanced role-based permissions
- Analytics or recommendation engines
