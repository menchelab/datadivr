# Technical Overview

This page documents all technologies, design patterns, tools, and practices used in datadivr.

## Core Technologies

### WebSocket

- **What**: Full-duplex communication protocol over TCP
- **Usage**: Primary communication protocol for real-time data exchange
- **Libraries**:
  - `websockets` (client-side)
  - `fastapi` (server-side)
- [Learn More](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

### FastAPI

- **What**: Modern, fast web framework for building APIs with Python
- **Version**: ≥0.115.4
- **Usage**: Powers the WebSocket server implementation
- **Benefits**:
  - Automatic OpenAPI docs
  - Native async support
  - Built-in WebSocket support
  - Type checking integration
- [Learn More](https://fastapi.tiangolo.com/)

### Pydantic

- **What**: Data validation using Python type annotations
- **Version**: ≥2.0.0
- **Usage**: Message validation and serialization
- **Benefits**:
  - Automatic validation
  - JSON serialization
  - OpenAPI schema generation
  - Type hints integration
- [Learn More](https://docs.pydantic.dev/)

## Development Tools

### uv

- **What**: Modern Python package installer and resolver
- **Usage**: Primary package management and virtual environment tool
- **Benefits**:
  - Faster than pip
  - Better dependency resolution
  - Built-in virtual environment management
  - Compatible with pip requirements
- [Learn More](https://github.com/astral-sh/uv)

### pre-commit

- **What**: Git hook framework
- **Version**: ≥2.20.0
- **Usage**: Automated code quality checks before commits
- **Hooks**:
  - Ruff (linting and formatting)
  - mypy (type checking)
  - YAML/TOML validation
  - Trailing whitespace removal
  - Merge conflict checks
  - Prettier (markdown/yaml formatting)
- [Learn More](https://pre-commit.com/)

### Ruff

- **What**: Fast Python linter and formatter
- **Version**: ≥0.6.9
- **Configuration**:
  - Target Python: 3.9+
  - Line length: 120
  - Enabled rule sets:
    - flake8-2020 (YTT)
    - flake8-bandit (S)
    - flake8-bugbear (B)
    - flake8-builtins (A)
    - flake8-comprehensions (C4)
    - flake8-debugger (T10)
    - flake8-simplify (SIM)
    - isort (I)
    - mccabe (C90)
    - pycodestyle (E, W)
    - pyflakes (F)
    - pygrep-hooks (PGH)
    - pyupgrade (UP)
    - tryceratops (TRY)
- [Learn More](https://github.com/astral-sh/ruff)

### mypy

- **What**: Static type checker for Python
- **Version**: ≥0.991
- **Configuration**:
  - Strict mode enabled
  - Disallow untyped definitions
  - No implicit optional
  - Warn on unused ignores
  - Show error codes
- [Learn More](https://mypy.readthedocs.io/)

## Testing Tools

### pytest

- **What**: Python testing framework
- **Version**: ≥7.2.0
- **Features**:
  - Fixtures
  - Parameterization
  - Async support
  - Coverage reporting
- **Plugins**:
  - pytest-cov (≥4.0.0)
  - pytest-asyncio (≥0.24.0)
- [Learn More](https://docs.pytest.org/)

### tox

- **What**: Test automation and virtual environment management
- **Version**: tox-uv ≥1.11.3
- **Configuration**:
  - Python versions: 3.9-3.13
  - Runs pytest with coverage
  - Runs mypy type checking
  - GitHub Actions integration
- [Learn More](https://tox.wiki/)

### Coverage.py

- **What**: Code coverage measurement
- **Usage**: Track test coverage metrics
- **Configuration**:
  - Branch coverage enabled
  - Skip empty files
  - Source package: datadivr
- [Learn More](https://coverage.readthedocs.io/)

## CI/CD Pipeline

### GitHub Actions

- **What**: Continuous Integration/Deployment platform
- **Workflows**:
  1. Quality Checks (`main.yml`):
     - Pre-commit validation
     - Unit tests (Python 3.9-3.13)
     - Type checking with mypy
     - Coverage reporting to Codecov
     - Documentation build verification
  2. Release Process (`on-release-main.yml`):
     - Version updating
     - PyPI package publishing
     - Documentation deployment
  3. Configuration Validation:
     - Codecov configuration validation
- [Learn More](https://docs.github.com/en/actions)

### Codecov

- **What**: Code coverage reporting service
- **Usage**: Track and visualize test coverage
- **Features**:
  - PR comments
  - Coverage trends
  - Configuration validation
- [Learn More](https://codecov.io/)

## Documentation

### MkDocs

- **What**: Static site generator for documentation
- **Version**: ≥1.4.2
- **Theme**: Material for MkDocs (≥8.5.10)
- **Features**:
  - Navigation sections
  - Search suggestions
  - Content tabs
  - Dark/light mode
- [Learn More](https://www.mkdocs.org/)

### mkdocstrings

- **What**: Automatic documentation from docstrings
- **Version**: ≥0.26.1
- **Features**:
  - Python handler
  - Source code display
  - Category headings
  - Submodule documentation
- [Learn More](https://mkdocstrings.github.io/)

## Design Patterns

### Event-Driven Architecture

- **What**: Pattern where components communicate via events
- **Implementation**: WebSocket events and handlers
- **Benefits**:
  - Loose coupling
  - Scalability
  - Real-time communication

### Decorator Pattern

- **What**: Dynamically add behavior to objects
- **Usage**: `@websocket_handler` for event registration
- **Benefits**:
  - Clean handler registration
  - Separation of concerns
  - Runtime flexibility

### Registry Pattern

- **What**: Central registry for components
- **Usage**: Handler registration system
- **Benefits**:
  - Dynamic handler discovery
  - Centralized management
  - Runtime registration

### Factory Pattern

- **What**: Object creation abstraction
- **Usage**: Message creation utilities
- **Benefits**:
  - Consistent message creation
  - Encapsulation
  - Flexible object creation

## Python Support

- **Required Version**: ≥3.9, <4.0
- **Tested Versions**:
  - Python 3.9
  - Python 3.10
  - Python 3.11
  - Python 3.12
  - Python 3.13

## Dependencies

### Runtime Dependencies

- fastapi ≥0.115.4
- prompt-toolkit ≥3.0.48
- rich ≥13.9.4
- typer ≥0.13.0
- uvicorn ≥0.32.0
- websockets ≥13.1
- pydantic ≥2.0.0
- structlog ≥23.1.0

### Development Dependencies

All development dependencies are managed through uv and specified in pyproject.toml.
