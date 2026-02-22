# AGENTS.md — flagsmith

## Project Overview

Flagsmith is an open-source feature flagging and remote configuration management tool. It allows teams to manage feature releases, perform A/B testing, and toggle application functionality without deploying new code. The tech stack is centered around a Python/Django backend API and a TypeScript/React single-page application frontend, designed to be self-hosted with Docker or used as a SaaS product.

## Tech Stack

-   **Languages**: Python, TypeScript
-   **Frameworks**: Django, Django REST Framework, React, Redux Toolkit
-   **Database**: PostgreSQL
-   **Dependency Management**: Poetry (Backend), npm (Frontend)
-   **Testing**: `pytest` (Backend Unit & Integration), Jest (Frontend Unit), TestCafe (Frontend E2E)
-   **Formatting & Linting**: `black`, `isort` (Backend); Prettier, ESLint (Frontend)
-   **DevOps & Infrastructure**: Docker, Docker Compose
-   **Error Monitoring**: Sentry, Prometheus

## Architecture

The project uses a monorepo structure, separating the backend, frontend, and documentation into distinct top-level directories. It follows a client-server model with a monolithic Django API and a React Single-Page Application (SPA).

-   `api/`: The monolithic Django backend.
    -   `api/features/`, `api/organisations/`, `api/users/`: Modular Django apps, each containing its own models, views, and serializers, promoting separation of concerns.
    -   `api/tests/`: Contains all backend tests, subdivided into `unit/` and `integration/`.
    -   `api/pyproject.toml`: Defines all Python dependencies managed by Poetry.
-   `frontend/`: The React SPA frontend.
    -   `frontend/web/`: Main source code for the application.
    -   `frontend/web/components/`: Reusable React components form the core of the UI.
    -   `frontend/common/`: Contains shared logic, including state management.
    -   `frontend/common/store.ts`: The central Redux Toolkit store configuration.
    -   `frontend/common/service.ts`: The single RTK Query service definition that handles all API communication.
    -   `frontend/e2e/`: End-to-end tests written with TestCafe.
    -   `frontend/package.json`: Defines all frontend dependencies managed by npm.
-   `docs/`: Project documentation built with Docusaurus.
-   `docker-compose.yml`: The entry point for setting up the entire local development environment.

## Code Style

The codebase maintains a strict and consistent style through automated formatters and linters.

**Backend (Python):**
-   **Formatting**: Code is formatted with `black` and imports are sorted with `isort`. These tools are configured in `api/pyproject.toml` and must be run before committing.
-   **Naming**: Follows standard Python PEP 8 conventions (e.g., `snake_case` for variables and functions, `PascalCase` for classes).
-   **Views**: Class-based views are used, inheriting from Django REST Framework's `APIView`. Business logic should not reside in the view itself but be abstracted into model methods or service functions.

Example of a backend view (`api/audit/views.py`):
```python
from rest_framework.response import Response
from rest_framework.views import APIView
from audit.models import AuditLog

class AuditLogCount(APIView):
    def get(self, request, *args, **kwargs):
        count = AuditLog.objects.count()
        return Response({'count': count})
```

**Frontend (TypeScript/React):**
-   **Formatting**: Code is automatically formatted using **Prettier**.
-   **Linting**: **ESLint** is used to enforce code quality and best practices.
-   **Components**: Functional components with Hooks are standard.
-   **Data Fetching**: All data fetching is done via auto-generated RTK Query hooks.

Example of a frontend component (`frontend/web/components/AuditLogCounter.tsx`):
```typescript
import React from 'react';
import { useGetAuditLogCountQuery } from 'common/service';

export const AuditLogCounter = () => {
    const { data, isLoading, error } = useGetAuditLogCountQuery({});

    if (isLoading) return <div>Loading...</div>;
    if (error) return <div>Error fetching count!</div>;

    return <h1>Total Audit Logs: {data?.count}</h1>;
};
```

## Anti-Patterns & Restrictions

To maintain architectural integrity and code quality, the following rules must be strictly followed:

-   **Frontend:**
    -   **NEVER** make direct API calls from components using `fetch` or `axios`. **ALWAYS** use the RTK Query service layer defined in `frontend/common/service.ts`.
    -   **NEVER** introduce a new global state management library. All global state must be managed via the existing Redux Toolkit store (`frontend/common/store.ts`).

-   **Backend:**
    -   **NEVER** bypass the Django ORM for database operations unless it is for a critical, well-documented performance optimization.
    -   **AVOID** placing complex business logic directly within Django views (`views.py`). This logic should be abstracted into separate service functions or model methods to keep views lean and focused on handling the HTTP request/response cycle.

## Database & State Management

The application manages state and data flow differently on the backend and frontend.

**Backend (Database):**
-   The primary database is **PostgreSQL**.
-   All database interactions are handled exclusively through the **Django ORM**. Direct SQL queries are forbidden except in rare, documented cases.
-   Database schemas are defined as Django models within each app's `models.py` file (e.g., `api/features/models.py`).
-   Schema changes must be managed through Django's migration system. New migrations are created with `poetry run python manage.py makemigrations` and applied with `poetry run python manage.py migrate`.

**Frontend (State):**
-   **Server State & Caching**: All interactions with the backend API (fetching, creating, updating, deleting data) are managed by **RTK Query**. The API service definition is located in `frontend/common/service.ts`. This provides hooks that handle the entire data lifecycle, including caching, invalidation, and optimistic updates.
-   **Global UI State**: Global state that is not persisted on the server (e.g., modal visibility, UI themes) is managed by **Redux Toolkit**. The store is configured in `frontend/common/store.ts`. New state is added by creating a new "slice" with `createSlice`.

## Error Handling & Logging

-   **Backend**:
    -   **Logging**: Uses Python's standard `logging` module, configured in `api/app/settings/common.py`. Logs should be used to record important events and debug issues.
    -   **Error Reporting**: In production, unhandled exceptions are captured and reported to **Sentry**. The Sentry integration is configured via environment variables.

-   **Frontend**:
    -   **Error Reporting**: Unhandled client-side exceptions are captured and sent to **Sentry**.
    -   **Error Boundaries**: Components that have a high chance of failing or depend on fragile data should be wrapped in React **Error Boundaries**. This prevents a component-level error from crashing the entire application and allows a fallback UI to be displayed.

## Testing Commands

-   **Run the full application stack (API, Frontend, DB):**
    ```bash
    docker-compose up
    ```
-   **Build and run the stack from scratch:**
    ```bash
    docker-compose up --build
    ```
-   **Run backend tests:**
    ```bash
    cd api
    poetry run pytest
    ```
-   **Run frontend linter:**
    ```bash
    cd frontend
    npm run lint
    ```
-   **Run frontend dev server (with Hot Module Replacement):**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

## Testing Guidelines

**Backend (`pytest`):**
-   All test files are located in the `api/tests/` directory.
-   Test files should be named following the `test_*.py` pattern.
-   **Unit Tests**: Located in `api/tests/unit/`. These tests should focus on a single function or class and mock external dependencies (like database or network calls) where necessary.
-   **Integration Tests**: Located in `api/tests/integration/`. These tests verify the interaction between different components of the backend, often involving database access.
-   Fixtures are heavily used to set up test data and clients. For example, `admin_client` provides an authenticated API client.

Example backend test (`api/tests/unit/audit/test_views.py`):
```python
def test_get_audit_log_count(admin_client):
    # When
    response = admin_client.get("/api/v1/audit/count/")
    # Then
    assert response.status_code == 200
    assert response.json()["count"] >= 0
```

**Frontend (`Jest` & `TestCafe`):**
-   **Unit/Component Tests (`Jest`)**: Test files should be co-located with the components they are testing (e.g., `Component.tsx` and `Component.test.tsx`). These tests should verify component rendering and behavior in isolation.
-   **End-to-End Tests (`TestCafe`)**: E2E test scripts are located in the `frontend/e2e/` directory. These tests simulate real user workflows by interacting with the application in a browser.

## Security & Compliance

-   **Secrets Management**: **NEVER** hard-code secrets (API keys, passwords, tokens) in the source code. All secrets must be managed through environment variables. The `docker-compose.yml` file serves as a reference for required variables in local development.
-   **Authentication**: The API uses a built-in authentication system to protect endpoints.
-   **Authorization**: Permissions are managed using a Role-Based Access Control (RBAC) model to ensure users can only access resources appropriate for their role.
-   **Vulnerability Reporting**: Any discovered security vulnerabilities must be reported privately to `support[at]flagsmith[dot]com`. Do not disclose them publicly in GitHub issues.

## Dependencies & Environment

The entire development environment is containerized with Docker to ensure consistency.

-   **Runtime Environment**: The primary way to run the project is via Docker. `docker-compose up` will start all required services (backend, frontend, database).
-   **Backend Dependencies (Python)**:
    -   Managed by **Poetry**.
    -   Defined in `api/pyproject.toml`.
    -   To install: `cd api && poetry install`
    -   To add a new dependency: `cd api && poetry add <package-name>`
-   **Frontend Dependencies (JavaScript/TypeScript)**:
    -   Managed by **npm**.
    -   Defined in `frontend/package.json`.
    -   To install: `cd frontend && npm install`
    -   To add a new dependency: `cd frontend && npm install <package-name>`
-   **Environment Variables**: The application is configured using environment variables. See `docker-compose.yml` for a list of variables needed for local development.

## PR & Git Rules

The project follows a standard GitHub feature-branch workflow.

-   **Branch Naming**: Branch names should be descriptive and prefixed with a type, such as `feature/`, `bugfix/`, or `chore/`. Example: `feature/new-audit-log-export`.
-   **Commit Messages**: Commits should be atomic and have clear, descriptive messages explaining the "what" and "why" of the change.
-   **Workflow**:
    1.  First, create a GitHub Issue to discuss the proposed change.
    2.  Create a feature branch from an up-to-date `main` branch.
        ```bash
        git checkout main
        git pull origin main
        git checkout -b feature/my-new-feature
        ```
    3.  Implement changes and add corresponding tests.
    4.  Ensure all code is formatted and linted correctly.
    5.  Push the branch to your fork and open a Pull Request (PR) against the `flagsmith/flagsmith:main` branch.
    6.  The PR must be linked to the issue it resolves and must pass all Continuous Integration (CI) checks before it can be considered for merging.

## Documentation Standards

-   **System & User Documentation**: The public-facing documentation for users and administrators is maintained in the `/docs` directory and built with **Docusaurus**. Significant changes to functionality should be accompanied by updates to this documentation.
-   **Code Documentation**:
    -   **Python**: Use **docstrings** for public modules, classes, and functions to explain their purpose, arguments, and return values.
    -   **TypeScript/React**: Use **TSDoc** comments (`/** ... */`) to document complex components, props, and functions.

## Common Patterns

-   **Backend: Service Layer Abstraction**: Avoid putting business logic directly in Django views. Abstract complex operations into service functions or model methods. This keeps views thin and focused on HTTP concerns.
    ```python
    # Good: Logic is in the model/manager
    class AuditLogCount(APIView):
        def get(self, request, *args, **kwargs):
            # The 'how' is hidden from the view
            count = AuditLog.objects.get_total_count()
            return Response({'count': count})

    # Bad: Logic is coupled to the view
    class AuditLogCount(APIView):
        def get(self, request, *args, **kwargs):
            # Complex filtering and counting logic here...
            count = AuditLog.objects.filter(is_archived=False).count()
            return Response({'count': count})
    ```
-   **Frontend: Declarative Data Fetching**: **ALWAYS** use the RTK Query service for all API interactions. This pattern centralizes data fetching logic, provides automatic caching, and simplifies component code by using hooks.
    ```typescript
    // In frontend/common/service.ts
    getAuditLogCount: builder.query<{ count: number }, {}>({
        query: () => ({ url: `audit/count/` }),
    }),

    // In a React component
    import { useGetAuditLogCountQuery } from 'common/service';

    const MyComponent = () => {
      // The hook handles loading, error, and data states automatically
      const { data } = useGetAuditLogCountQuery({});
      return <div>Count: {data?.count}</div>;
    }
    ```
-   **Full-Stack Development**: New features typically require coordinated changes in both the `api/` and `frontend/` directories. This involves adding a DRF endpoint, serializing data, adding the endpoint to the RTK Query service, and creating a React component to consume it.

## Agent Workflow / SOP

When approaching a task, follow this Standard Operating Procedure (SOP):

1.  **Analyze the Request**: Determine if the task is backend-only, frontend-only, or full-stack.
2.  **Identify Key Files**:
    -   **Backend**: Locate the relevant Django app in `api/`. Changes will likely involve `models.py`, `serializers.py`, `views.py`, and `urls.py`. Tests will be in `api/tests/`.
    -   **Frontend**: For UI changes, find the component in `frontend/web/components/`. For data/state changes, the primary files are `frontend/common/service.ts` (API interaction) and `frontend/common/store.ts` (global UI state).
3.  **Implement Backend Changes (if required)**:
    -   Modify the Django model in `models.py` and create a migration (`poetry run python manage.py makemigrations`).
    -   Create or update a serializer in `serializers.py` to control the JSON representation.
    -   Create or update the view in `views.py`. Keep business logic out of the view.
    -   Register the URL route in `urls.py`.
    -   Write unit or integration tests in `api/tests/` to cover the new logic.
4.  **Implement Frontend Changes (if required)**:
    -   If a new API endpoint is involved, add it to the `builder` in `frontend/common/service.ts`.
    -   In the relevant React component, use the auto-generated RTK Query hook (e.g., `useGetMyDataQuery`) to fetch or mutate data.
    -   **Strictly avoid** using `fetch()` or `axios()` directly in components.
    -   Update or create React components to display the new data or provide new functionality.
    -   Add Jest unit tests for new components or complex logic.
5.  **Format and Lint**: Before finalizing, run the formatters and linters to ensure code style compliance.
    -   Backend: `black .` and `isort .` within the `api/` directory.
    -   Frontend: `npm run lint` within the `frontend/` directory.
6.  **Verify Locally**: Use `docker-compose up --build` to run the entire application and manually verify that your changes work as expected end-to-end.

## Few-Shot Examples

### Good: Following the RTK Query Pattern for Data Fetching

This example correctly uses the centralized RTK Query service to fetch data and display it in a component.

**1. Define the endpoint in `frontend/common/service.ts`:**
```typescript
// Good: The endpoint definition is centralized and declarative.
getAuditLogCount: builder.query<{ count: number }, {}>({
    query: () => ({
        url: `audit/count/`,
    }),
}),
```

**2. Use the generated hook in `frontend/web/components/AuditLogCounter.tsx`:**
```typescript
import React from 'react';
import { useGetAuditLogCountQuery } from 'common/service';

// Good: The component is simple, declarative, and leverages the hook for all async logic.
export const AuditLogCounter = () => {
    const { data, isLoading, error } = useGetAuditLogCountQuery({});

    if (isLoading) return <div>Loading...</div>;
    if (error) return <div>Error fetching count!</div>;

    return <h1>Total Audit Logs: {data?.count}</h1>;
};
```

### Bad: Bypassing the RTK Query Service Layer

This example violates the core architectural rule by making a direct API call from a component.

**`frontend/web/components/AuditLogCounter.tsx`:**
```typescript
import React, { useEffect, useState } from 'react';

// Bad: This component violates the rule against direct API calls.
// It manually handles loading, error, and data states, which is redundant
// and inconsistent with the rest of the application.
export const AuditLogCounter = () => {
    const [data, setData] = useState<{ count: number } | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        // DO NOT DO THIS. Use the RTK Query service instead.
        fetch('http://localhost:8000/api/v1/audit/count/')
            .then(res => res.json())
            .then(setData)
            .catch(setError)
            .finally(() => setIsLoading(false));
    }, []);

    if (isLoading) return <div>Loading...</div>;
    if (error) return <div>Error fetching count!</div>;

    return <h1>Total Audit Logs: {data?.count}</h1>;
};
