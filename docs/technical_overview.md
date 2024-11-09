# Technical Overview

This page documents the key technologies, design patterns, and tools used in datadivr.

## Core Technologies

### WebSocket

- **What**: Full-duplex communication protocol over TCP
- **Usage**: Primary communication protocol for real-time data exchange
- **Library**: `websockets` for client, `fastapi` for server
- [Learn More](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

### FastAPI

- **What**: Modern, fast web framework for building APIs with Python
- **Usage**: Powers the WebSocket server implementation
- **Benefits**: Automatic OpenAPI docs, async support, type checking
- [Learn More](https://fastapi.tiangolo.com/)

### Pydantic

- **What**: Data validation using Python type annotations
- **Usage**: Message validation and serialization
- **Benefits**: Automatic validation, serialization, and documentation
- [Learn More](https://docs.pydantic.dev/)

## Development Tools

### uv

- **What**: Modern Python package installer and resolver
- **Usage**: Primary package management and virtual environment tool
- **Benefits**: Faster than pip, better dependency resolution
- [Learn More](https://github.com/astral-sh/uv)

### pre-commit

- **What**: Git hook framework
- **Usage**: Automated code quality checks before commits
- **Hooks**:
  - Ruff (linting)
  - mypy (type checking)
  - YAML/TOML validation
  - Prettier (formatting)
- [Learn More](https://pre-commit.com/)

### Ruff

- **What**: Fast Python linter and formatter
- **Usage**: Code style enforcement and automatic fixes
- **Benefits**: Combines multiple tools (flake8, isort, etc.)
- [Learn More](https://github.com/astral-sh/ruff)

### mypy

- **What**: Static type checker for Python
- **Usage**: Type checking during development and CI
- **Benefits**: Catch type-related errors early
- [Learn More](https://mypy.readthedocs.io/)

## Testing Tools

### pytest

- **What**: Python testing framework
- **Usage**: Unit tests and test coverage
- **Features**: Fixtures, parameterization, async support
- [Learn More](https://docs.pytest.org/)

### tox

- **What**: Test automation and virtual environment management
- **Usage**: Testing against multiple Python versions
- **Integration**: GitHub Actions for CI
- [Learn More](https://tox.wiki/)

### Coverage.py

- **What**: Code coverage measurement
- **Usage**: Track test coverage metrics
- **Integration**: Codecov for reporting
- [Learn More](https://coverage.readthedocs.io/)

## CI/CD Pipeline

### GitHub Actions

- **What**: Continuous Integration/Deployment platform
- **Workflows**:
  1. Quality Checks (`main.yml`):
     - Pre-commit validation
     - Unit tests (Python 3.9-3.13)
     - Type checking
     - Coverage reporting
  2. Release Process (`on-release-main.yml`):
     - Version updates
     - PyPI publishing
     - Documentation deployment
- [Learn More](https://docs.github.com/en/actions)

### Codecov

- **What**: Code coverage reporting service
- **Usage**: Track and visualize test coverage
- **Features**: PR comments, coverage trends
- [Learn More](https://codecov.io/)

## Documentation

### MkDocs

- **What**: Static site generator for documentation
- **Usage**: Project documentation
- **Theme**: Material for MkDocs
- [Learn More](https://www.mkdocs.org/)

### mkdocstrings

- **What**: Automatic documentation from docstrings
- **Usage**: API reference generation
- **Benefits**: Keep docs and code in sync
- [Learn More](https://mkdocstrings.github.io/)

## Design Patterns

### Event-Driven Architecture

- **What**: Pattern where components communicate via events
- **Implementation**: WebSocket events and handlers
- **Benefits**: Loose coupling, scalability

### Decorator Pattern

- **What**: Dynamically add behavior to objects
- **Usage**: `@websocket_handler` for event registration
- **Benefits**: Clean handler registration, separation of concerns

### Registry Pattern

- **What**: Central registry for components
- **Usage**: Handler registration system
- **Benefits**: Dynamic handler discovery and management

### Factory Pattern

- **What**: Object creation abstraction
- **Usage**: Message creation utilities
- **Benefits**: Consistent message creation, encapsulation
