# BACKEND CLEAN ARCHITECTURE RULES

All backend development MUST follow **Clean Architecture** principles to ensure independence from frameworks, databases, and external tools.

## 🏗️ Layered Architecture

The backend is organized into four logical layers, following the **Dependency Rule**: *Dependencies point only inwards.*

### 1. Domain Layer (The Core)
- **Location**: `src/domain/`
- **Contents**:
    - **Entities**: Core business objects and logic.
    - **Repository Interfaces**: Abstract definitions of data access.
    - **Exceptions**: Domain-specific errors.
- **Rule**: This layer MUST NOT depend on any other layer or any external library (besides standard Python). NO imports from `fastapi`, `sqlalchemy`, etc.

### 2. Application Layer (Business Logic)
- **Location**: `src/application/`
- **Contents**:
    - **Use Cases (Interactors)**: Orchestrate the flow of data to and from entities.
    - **DTOs (Data Transfer Objects)**: Input/Output models for use cases.
- **Rule**: Depends ONLY on the **Domain** layer.

### 3. Infrastructure Layer (Implementation)
- **Location**: `src/infrastructure/`
- **Contents**:
    - **Repositories**: Concrete implementations of Domain interfaces.
    - **Database**: SQL/NoSQL configurations and sessions.
    - **External Services**: API clients, messaging systems.
- **Rule**: Depends on **Domain** and **Application** layers. This is where frameworks (e.g., SQLAlchemy, Redis) are integrated.

### 4. Presentation Layer (API / Entry Points)
- **Location**: `src/presentation/`
- **Contents**:
    - **Routes**: FastAPI path operations.
    - **Schemas**: Pydantic models for Request/Response validation.
    - **Middlewares**: Auth, logging, error handling.
- **Rule**: Depends on **Application** (to call use cases) and **Infrastructure** (for dependency injection).

## 📂 Visual Hierarchy

```text
src/
  ├── domain/         # Entities & Interfaces (No dependencies)
  ├── application/    # Use Cases (Depends on Domain)
  ├── infrastructure/ # DB & Implementations (Depends on Domain/Application)
  └── presentation/   # FastAPI & Schemas (Depends on Application/Infrastructure)
```

## 🛠️ Implementation Rules

1.  **Dependency Inversion**: Use interfaces in the Domain layer. Inject implementations from the Infrastructure layer into Use Cases.
2.  **Model Separation**:
    - **Domain Entities**: Plain Python classes for logic.
    - **Database Models**: SQLAlchemy/Tortoise models for persistence.
    - **API Schemas**: Pydantic models for validation.
    - *Mapping must occur when moving data between layers.*
3.  **Thin Controllers**: FastAPI routes should only handle request parsing, call a Use Case, and return the result. No business logic in routes.
4.  **No Leaky Abstractions**: Infrastructure details (like SQL specific types) must not leak into the Domain or Application layers.
