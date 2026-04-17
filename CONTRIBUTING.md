# Contributing to Semantic Toolkit

Thank you for your interest in contributing to Semantic Toolkit! This guide will help you get started with development.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- `uv` (fast Python package manager) - install with: `pip install uv`
- Git

### Setting Up the Development Environment

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/semantic-toolkit.git
   cd semantic-toolkit
   ```

2. **Install dependencies with uv**

   ```bash
   uv sync
   ```

   This will install all dependencies from `pyproject.toml` and create a virtual environment automatically.

3. **Activate the virtual environment**

   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

### Running the Application

**Development mode with hot reload:**

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

**Access the interactive API documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
semantic-toolkit/
├── app/                    # Application source code
│   ├── main.py            # FastAPI application entry point
│   └── ...                # Other modules
├── tests/                 # Test files
├── pyproject.toml         # Project configuration and dependencies
└── README.md             # Project documentation
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_example.py

# Run tests with verbose output
pytest -v
```

### Adding Dependencies

```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name
```

## Making Changes

1. **Create a new branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Add or modify code in the `app/` directory
   - Add tests in the `tests/` directory
   - Ensure all tests pass with `pytest`

3. **Commit your changes**

   ```bash
   git add .
   git commit -m "Describe your changes"
   ```

4. **Push to your branch**

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**
   - Go to the repository on GitHub
   - Click "New Pull Request"
   - Describe your changes and submit

## Coding Guidelines

- Write descriptive commit messages
- Add tests for new features
- Keep functions small and focused
- Document complex logic with comments

## Adding New Features

1. Create a new branch for your feature
2. Add your code to the appropriate module in `app/`
3. Add corresponding tests in `tests/`
4. Update documentation if needed
5. Ensure all tests pass with `pytest`
6. Submit a pull request

## Reporting Issues

If you find a bug or have a feature request:

1. Check existing issues first
2. Create a new issue with:
   - Clear title
   - Detailed description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Environment details (Python version, OS, etc.)

## Questions?

If you have questions about contributing:

- Read the code and existing tests
- Check existing issues and pull requests
- Open an issue with your question

Happy coding! 🚀
