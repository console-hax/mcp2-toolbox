# Contributing to mcp2-toolbox

Thank you for your interest in contributing to mcp2-toolbox! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Git
- Basic understanding of Python development

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/your-username/mcp2-toolbox.git
   cd mcp2-toolbox
   ```

2. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Run tests to ensure everything works**:
   ```bash
   pytest
   ```

## Development Workflow

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Critical fixes

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards below

3. **Add tests** for new functionality

4. **Run the test suite**:
   ```bash
   pytest
   ```

5. **Check code quality**:
   ```bash
   black mcp2_toolbox/
   flake8 mcp2_toolbox/
   mypy mcp2_toolbox/
   ```

6. **Commit your changes** with descriptive messages

7. **Push and create a pull request**

## Coding Standards

### Python Code

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write docstrings for all public functions and classes
- Keep functions small and focused
- Use meaningful variable and function names

### Code Formatting

We use `black` for code formatting:
```bash
black mcp2_toolbox/
```

### Linting

We use `flake8` for linting:
```bash
flake8 mcp2_toolbox/
```

### Type Checking

We use `mypy` for type checking:
```bash
mypy mcp2_toolbox/
```

## Testing

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies
- Aim for high test coverage

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp2_toolbox --cov-report=html

# Run specific test file
pytest tests/test_cli.py

# Run specific test
pytest tests/test_cli.py::TestDevice::test_device_creation
```

## Documentation

### Code Documentation

- Write docstrings for all public functions and classes
- Use Google-style docstrings
- Include examples in docstrings when helpful

### README Updates

- Update the README when adding new features
- Include usage examples
- Update installation instructions if needed

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**
2. **Check code quality** (formatting, linting, type checking)
3. **Update documentation** as needed
4. **Add tests** for new functionality
5. **Update CHANGELOG.md** with your changes

### Pull Request Template

When creating a pull request, please include:

- **Description**: What changes were made and why
- **Testing**: How the changes were tested
- **Breaking Changes**: Any breaking changes and migration steps
- **Screenshots**: If applicable for UI changes

### Review Process

- All pull requests require review
- Address feedback promptly
- Keep pull requests focused and small
- Respond to review comments constructively

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the issue
- **Steps to Reproduce**: Detailed steps to reproduce the bug
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, etc.
- **Logs**: Relevant error messages or logs

### Feature Requests

When requesting features, please include:

- **Description**: Clear description of the feature
- **Use Case**: Why this feature would be useful
- **Proposed Solution**: How you think it should work
- **Alternatives**: Other solutions you've considered

## Release Process

### Version Numbering

We follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version number updated
- [ ] Release notes prepared

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Expected Behavior

- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, trolling, or discrimination
- Personal attacks or political discussions
- Spam or off-topic discussions
- Publishing private information without permission

## Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For general questions and discussions
- **Email**: For security issues (see SECURITY.md)

## License

By contributing to mcp2-toolbox, you agree that your contributions will be licensed under the same license as the project.

Thank you for contributing to mcp2-toolbox!
