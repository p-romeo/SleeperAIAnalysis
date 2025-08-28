# Contributing to Sleeper AI Lineup Optimizer

Thank you for your interest in contributing to the Sleeper AI Lineup Optimizer! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **🐛 Bug Reports**: Report bugs and issues
- **✨ Feature Requests**: Suggest new features
- **📝 Documentation**: Improve documentation
- **🧪 Testing**: Write tests or report test results
- **💻 Code**: Submit code improvements
- **🎨 UI/UX**: Improve user interface and experience
- **🔧 Infrastructure**: Help with CI/CD, deployment, etc.

### Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/sleeper-ai-lineup-optimizer.git
   cd sleeper-ai-lineup-optimizer
   ```
3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes**
5. **Test your changes**
6. **Commit your changes**
   ```bash
   git commit -m "feat: add new feature description"
   ```
7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Create a Pull Request**

## 🏗️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- pip

### Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

2. **Setup pre-commit hooks**
   ```bash
   pre-commit install
   ```

3. **Verify installation**
   ```bash
   python -m src.main --help
   ```

### Development Tools

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pytest**: Testing
- **Pre-commit**: Git hooks

## 📝 Code Style

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line length**: 88 characters (Black default)
- **Type hints**: Required for all public functions
- **Docstrings**: Use Google-style docstrings
- **Imports**: Group imports (standard library, third-party, local)

### Example Code Style

```python
from typing import List, Optional
from pathlib import Path

from .base import BaseClass
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ExampleClass(BaseClass):
    """Example class demonstrating code style."""
    
    def __init__(self, name: str, items: Optional[List[str]] = None) -> None:
        """
        Initialize the example class.
        
        Args:
            name: The name of the instance
            items: Optional list of items
            
        Raises:
            ValueError: If name is empty
        """
        if not name:
            raise ValueError("Name cannot be empty")
        
        self.name = name
        self.items = items or []
        logger.info(f"Initialized {self.name} with {len(self.items)} items")
    
    def add_item(self, item: str) -> None:
        """Add an item to the list."""
        self.items.append(item)
        logger.debug(f"Added item: {item}")
    
    def get_items(self) -> List[str]:
        """Get all items."""
        return self.items.copy()
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m "unit"      # Unit tests only
pytest -m "integration"  # Integration tests only
pytest -m "slow"      # Slow tests only

# Run specific test file
pytest tests/test_utils.py

# Run specific test function
pytest tests/test_utils.py::TestAppConfig::test_default_values
```

### Writing Tests

- **Test coverage**: Aim for >90% coverage
- **Test organization**: Group related tests in classes
- **Test names**: Use descriptive names that explain the test
- **Mocking**: Use mocks for external dependencies
- **Fixtures**: Use pytest fixtures for common setup

### Example Test

```python
import pytest
from unittest.mock import patch, MagicMock

from src.utils.config import AppConfig


class TestAppConfig:
    """Test AppConfig class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = AppConfig()
        assert config.ai_provider == "mock"
        assert config.ai_api_key == ""
        assert config.sleeper_username == ""
    
    @patch('pathlib.Path.home')
    def test_config_file_path(self, mock_home):
        """Test configuration file path construction."""
        mock_home.return_value = Path("/fake/home")
        config = AppConfig()
        assert config.config_file == Path("/fake/home/.sleeper_optimizer/config.encrypted")
    
    def test_invalid_config(self):
        """Test configuration validation with invalid data."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            AppConfig(sleeper_username="")
```

## 🔍 Code Quality

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality:

- **Black**: Automatic code formatting
- **Flake8**: Linting and style checking
- **MyPy**: Type checking
- **Prettier**: Markdown formatting

### Manual Quality Checks

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Check types
mypy src/

# Check formatting
black --check src/ tests/
```

## 📚 Documentation

### Documentation Standards

- **README.md**: Project overview and quick start
- **Docstrings**: Google-style docstrings for all public functions
- **Type hints**: Comprehensive type annotations
- **Examples**: Include usage examples in docstrings

### Building Documentation

```bash
# Install documentation dependencies
pip install sphinx sphinx-rtd-theme

# Build documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

## 🚀 Pull Request Process

### Before Submitting

1. **Ensure tests pass**
   ```bash
   pytest
   ```

2. **Check code quality**
   ```bash
   black src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

3. **Update documentation** if needed

4. **Add tests** for new functionality

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Test addition
- [ ] Other (please describe)

## Testing
- [ ] All tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes
```

## 🐛 Bug Reports

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 10, macOS 12, Ubuntu 20.04]
- Python Version: [e.g., 3.9.7]
- Package Version: [e.g., 1.0.0]

## Additional Information
Any other relevant information
```

## ✨ Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the requested feature

## Use Case
Why this feature would be useful

## Proposed Implementation
How you think it could be implemented

## Alternatives Considered
Other approaches you've considered

## Additional Information
Any other relevant information
```

## 📋 Issue Labels

We use the following labels to categorize issues:

- **bug**: Something isn't working
- **enhancement**: New feature or request
- **documentation**: Improvements or additions to documentation
- **good first issue**: Good for newcomers
- **help wanted**: Extra attention is needed
- **question**: Further information is requested
- **wontfix**: This will not be worked on

## 🏷️ Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```bash
git commit -m "feat: add new AI provider support"
git commit -m "fix: resolve API timeout issue"
git commit -m "docs: update installation instructions"
git commit -m "test: add unit tests for config module"
```

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on the code, not the person
- Provide constructive feedback
- Help others learn and grow

### Communication

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Requests**: For code contributions
- **Discord/Slack**: For real-time collaboration (if available)

## 🎯 Getting Help

### Resources

- **Documentation**: Check the README and docstrings
- **Issues**: Search existing issues for similar problems
- **Discussions**: Ask questions in GitHub Discussions
- **Code**: Review the source code for examples

### Questions

If you have questions about contributing:

1. **Search existing issues** first
2. **Check the documentation**
3. **Ask in GitHub Discussions**
4. **Create a new issue** if needed

## 🙏 Recognition

Contributors will be recognized in:

- **README.md**: Contributors section
- **Release notes**: For significant contributions
- **GitHub**: Through the contributors graph
- **Documentation**: In relevant sections

---

Thank you for contributing to the Sleeper AI Lineup Optimizer! 🏈🤖

Your contributions help make fantasy football better for everyone!
