# Contributing to plantuml2drawio

Thank you for your interest in contributing to plantuml2drawio! This document provides guidelines and instructions for contributing.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/doubleSlash-net/plantuml2drawio.git
cd plantuml2drawio
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

## Development Guidelines

### Code Style

We use the following tools to ensure code quality:
- `black` for code formatting
- `isort` for import sorting
- `flake8` for linting
- `mypy` for type checking

Before submitting a PR, please run:
```bash
black .
isort .
flake8
mypy src/plantuml2drawio
```

### Testing

We use pytest for testing. To run tests:
```bash
pytest tests/
```

For coverage report:
```bash
pytest --cov=plantuml2drawio tests/
```

### Documentation

- All new features should include documentation
- Use Google-style docstrings
- Include type hints for all function parameters and return values

### Pull Request Process

1. Create a new branch for your feature/fix
2. Write tests for new functionality
3. Ensure all tests pass
4. Update documentation if needed
5. Submit a pull request

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
