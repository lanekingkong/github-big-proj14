# Contributing to OmniForge

We love contributions! Here's how you can help make OmniForge even better.

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Bugs

Before submitting a bug report:
1. **Check existing issues** - Your bug may already be reported
2. **Use the bug report template** - Include all required information
3. **Provide reproduction steps** - Clear, minimal reproduction is essential

**Issue Template:**
```markdown
### Bug Description
Brief description of the bug

### Steps to Reproduce
1. Install version '...'
2. Run '...'
3. See error

### Expected Behavior
What should happen

### Actual Behavior
What actually happens

### Environment
- OS: [e.g. Windows 11, macOS 14, Ubuntu 24.04]
- Python version: [e.g. 3.11.7]
- OmniForge version: [e.g. 1.0.0]
```

### Suggesting Features

We welcome feature suggestions! When suggesting a feature:
1. **Explain the problem** - What pain point does this solve?
2. **Describe the solution** - How would it work?
3. **Consider alternatives** - Are there other approaches?
4. **Provide use cases** - Who benefits from this?

### Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**:
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass
4. **Commit your changes**: Use [Conventional Commits](https://www.conventionalcommits.org/)
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `test:` for tests
   - `refactor:` for code changes
5. **Push to your fork**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**:
   - Reference any related issues
   - Describe your changes clearly
   - Include screenshots if applicable

### Development Setup

```bash
# Clone the repository
git clone https://github.com/lanekingkong/omniforge.git
cd omniforge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linting
black omniforge tests
ruff check omniforge tests
mypy omniforge
```

### Coding Standards

- **Python 3.11+** with type hints
- **Black** for code formatting (line length: 100)
- **Ruff** for linting
- **Mypy** for type checking (strict mode)
- **Pytest** for testing (minimum 80% coverage)

### Commit Message Convention

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`

### Documentation

- Keep README.md up to date
- Document all public APIs with docstrings
- Add examples for new features
- Update CHANGELOG.md

### Adding New Skills

1. Create skill in `skills/` directory
2. Add to `SKILLS.md` registry
3. Include tests in `tests/test_skills.py`
4. Update documentation

### Review Process

- All PRs require at least one review
- CI must pass before merging
- Changes must not break existing tests
- New features must include tests

## Project Structure Conventions

```
omniforge/
├── core/           # Core engine (high priority, strong tests required)
├── agents/         # Agent system (integration tests preferred)
├── trust/          # Security (security review required for changes)
├── fixer/          # Auto-fix (edge case testing required)
├── gate/           # Gateway (rate limit tests required)
├── mcp/            # MCP (protocol compliance tests)
├── integrations/   # Integrations (mock external services)
├── dashboard/      # Dashboard (UI regression tests)
├── skills/         # Skills marketplace
├── tests/          # All tests
└── examples/       # Usage examples
```

## Recognition

All contributors will be recognized in:
- The project README
- Release notes
- GitHub contributors graph

Thank you for contributing to OmniForge!