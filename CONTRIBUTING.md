# Contributing to Microsoft Purview Custom Connector Solution Accelerator

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Code of Conduct

This project follows the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).

## How to Contribute

### Reporting Issues

- Use the GitHub issue tracker
- Check if the issue already exists
- Provide detailed information:
  - Steps to reproduce
  - Expected behavior
  - Actual behavior
  - Environment details (OS, Python version, etc.)

### Suggesting Features

- Open a GitHub issue with the "enhancement" label
- Describe the feature and its use case
- Explain why it would be valuable

### Submitting Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/dixitox/MicrosoftPurviewCustomConectors.git
   cd MicrosoftPurviewCustomConectors
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the coding standards
   - Add tests for new functionality
   - Update documentation

4. **Test your changes**
   ```bash
   pytest tests/
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your feature branch
   - Provide a clear description

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Azure CLI (for testing)

### Setup

```bash
# Clone the repo
git clone https://github.com/dixitox/MicrosoftPurviewCustomConectors.git
cd MicrosoftPurviewCustomConectors

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e ./src/purview_connector_sdk[dev]
```

## Coding Standards

### Python Style

- Follow PEP 8
- Use Black for code formatting
- Use type hints
- Maximum line length: 100 characters

```bash
# Format code
black src/

# Check style
flake8 src/

# Type checking
mypy src/
```

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Update README.md if adding new features
- Add examples for new connectors

### Testing

- Write unit tests for new code
- Maintain test coverage above 80%
- Use pytest for testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

## Project Structure

```
.
├── src/purview_connector_sdk/   # Core SDK
│   ├── connectors/              # Connector implementations
│   ├── models/                  # Data models
│   └── utils/                   # Utilities
├── examples/                    # Example connectors
├── tests/                       # Test files
└── docs/                        # Documentation
```

## Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added for new functionality
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts

## Questions?

- Open a GitHub Discussion
- Check existing documentation
- Review closed issues for similar questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
