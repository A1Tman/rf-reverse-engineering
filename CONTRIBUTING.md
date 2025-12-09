# Contributing to RF Reverse Engineering Projects

Thank you for your interest in contributing to this RF reverse engineering repository! This document provides guidelines for contributions.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Guidelines](#development-guidelines)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)
- [Legal Considerations](#legal-considerations)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

### Our Standards

- **Educational Focus**: All contributions must maintain the educational and research nature of this repository
- **Safety First**: Code must not create safety hazards, especially for the Gazco fireplace project
- **Legal Compliance**: All work must comply with RF regulations and intellectual property laws
- **Respect**: Be respectful and constructive in all interactions

### Unacceptable Behavior

- Encouraging illegal use of RF transmission equipment
- Sharing code that violates safety standards
- Disrespecting contributors or maintainers
- Publishing sensitive information about security vulnerabilities without coordination

## How Can I Contribute?

### Reporting Bugs

**Before submitting a bug report:**
- Check existing issues to avoid duplicates
- Verify the bug with the latest code
- Collect relevant information (hardware, software versions, error messages)

**Bug Report Template:**
```markdown
**Description**: Brief description of the issue

**Hardware**:
- RfCat device model:
- Target device:
- Operating system:

**Steps to Reproduce**:
1. Step one
2. Step two
3. ...

**Expected Behavior**: What should happen

**Actual Behavior**: What actually happens

**Logs/Screenshots**: Relevant output or images
```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:
- Clear use case description
- Expected benefits
- Implementation considerations
- Any safety or legal implications

### Contributing Code

We welcome contributions in these areas:
- **Bug fixes**: Corrections to existing code
- **Documentation**: Improvements to README files, comments, guides
- **Testing**: Additional test cases and validation
- **Analysis Tools**: Utilities for RF signal analysis
- **Examples**: Additional usage examples
- **Home Automation**: Integration with HA platforms (Home Assistant, OpenHAB)

## Development Guidelines

### Python Code Standards

**Style Guide**: Follow PEP 8 Python style guidelines

**Code Quality**:
```python
# Good: Clear, documented, safe
def send_command(self, command, repeats=10):
    """
    Send RF command to device.

    Args:
        command (str): Binary command string
        repeats (int): Number of transmissions (default: 10)

    Returns:
        bool: True if successful, False otherwise

    Raises:
        ValueError: If command format is invalid
        RuntimeError: If radio not initialized
    """
    if not self._validate_command(command):
        raise ValueError(f"Invalid command format: {command}")

    try:
        data = self._encode_pwm(command)
        for _ in range(repeats):
            self.radio.RFxmit(data)
            time.sleep(0.01)
        return True
    except Exception as e:
        logging.error(f"Transmission failed: {e}")
        return False
```

**Bad Practices to Avoid**:
```python
# Bad: No validation, no error handling, unclear
def send(cmd):
    data = encode(cmd)
    radio.RFxmit(data * 10)  # Why 10? What if it fails?
```

### RF Safety Guidelines

**All RF transmission code must:**
1. **Validate parameters** before transmission
2. **Check device state** to prevent conflicts
3. **Limit duty cycle** to comply with regulations
4. **Handle errors gracefully** without continuous retries
5. **Document frequency and power** clearly

**Example - Safe Transmission**:
```python
class SafeRFController:
    MAX_DUTY_CYCLE = 0.1  # 10% max transmission time
    COOLDOWN_PERIOD = 1.0  # 1 second between bursts

    def __init__(self):
        self.last_transmission = 0
        self.transmission_time = 0

    def send_command(self, command):
        # Enforce cooldown
        elapsed = time.time() - self.last_transmission
        if elapsed < self.COOLDOWN_PERIOD:
            raise RuntimeError("Cooldown period not elapsed")

        # Check duty cycle
        if self.transmission_time > self.MAX_DUTY_CYCLE:
            raise RuntimeError("Duty cycle limit exceeded")

        # Safe transmission with timing
        start = time.time()
        self._transmit(command)
        self.transmission_time += time.time() - start
        self.last_transmission = time.time()
```

### Testing Requirements

**All code contributions must include:**

1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test complete workflows
3. **Safety Tests**: Verify safety checks work
4. **Hardware Tests**: Document testing with actual hardware

**Test Example**:
```python
import unittest
from unittest.mock import Mock, patch

class TestGazcoController(unittest.TestCase):
    def setUp(self):
        self.controller = GazcoController()
        self.controller.radio = Mock()

    def test_command_validation(self):
        """Test that invalid commands are rejected"""
        with self.assertRaises(ValueError):
            self.controller.send_command('invalid')

    def test_pwm_encoding(self):
        """Test PWM encoding produces correct output"""
        binary = '10000011101110010000100'
        expected = b'\x9bm\xa4\x9aI\xb4\xdbi\xb0'
        result = self.controller._encode_pwm(binary)
        self.assertEqual(result, expected)

    def test_duty_cycle_limit(self):
        """Test that duty cycle limits are enforced"""
        # Simulate rapid transmissions
        for _ in range(100):
            try:
                self.controller.send_command('on')
            except RuntimeError as e:
                self.assertIn('duty cycle', str(e).lower())
                return
        self.fail("Duty cycle limit not enforced")
```

### Documentation Standards

**All contributions must include appropriate documentation:**

#### Code Comments
```python
# Good: Explain WHY, not just WHAT
# Use PWM encoding with extended repeats for reliability
# Gazco devices require minimum 9 transmissions to respond
for _ in range(10):  # One extra for margin
    self.radio.RFxmit(data)
```

#### README Updates
- Update relevant README.md files if behavior changes
- Add examples for new features
- Update technical specifications if protocol changes
- Include photos/screenshots for hardware changes

#### Commit Messages
```
Format: <type>(<scope>): <description>

Types:
  feat: New feature
  fix: Bug fix
  docs: Documentation only
  test: Adding tests
  refactor: Code refactoring
  safety: Safety-related changes

Examples:
  feat(gazco): Add home assistant integration
  fix(sonte): Correct PWM timing for DOWN command
  docs(methodology): Add GNU Radio flowgraph examples
  safety(gazco): Add duty cycle limiting to prevent overheating
```

## Legal Considerations

### Before Contributing, Ensure:

1. **Original Work**: Your contribution is your original work or properly licensed
2. **No Proprietary Info**: No manufacturer trade secrets or confidential information
3. **RF Compliance**: Code complies with local RF regulations
4. **Safety Review**: Changes don't create safety hazards

### Intellectual Property

By contributing, you agree that:
- Your contributions will be licensed under the MIT License
- You have the right to submit the contributions
- Your contributions are your original creation or properly licensed

### Security Vulnerabilities

**If you discover a security vulnerability:**
1. **Do NOT** open a public issue
2. Email the maintainer privately
3. Provide details and potential impact
4. Allow time for fix before public disclosure

## Pull Request Process

### Before Submitting

- [ ] Code follows Python PEP 8 style guidelines
- [ ] All tests pass (run `pytest`)
- [ ] Documentation is updated
- [ ] Safety considerations are addressed
- [ ] Commit messages follow the format
- [ ] No secrets or API keys in code

### Submission Process

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feat/amazing-feature`)
3. **Commit** your changes with clear messages
4. **Push** to your fork (`git push origin feat/amazing-feature`)
5. **Open** a Pull Request with description

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Safety improvement

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Hardware tested (if applicable)

## Hardware Tested
- Device: [e.g., YARD Stick One]
- Target: [e.g., Gazco fireplace]
- Results: [e.g., All commands work correctly]

## Safety Checklist
- [ ] No safety hazards introduced
- [ ] Duty cycle limits respected
- [ ] Error handling implemented
- [ ] Documentation includes warnings

## Legal Checklist
- [ ] Original work or properly licensed
- [ ] No proprietary information
- [ ] Complies with RF regulations
- [ ] MIT License terms accepted
```

### Review Process

**Maintainers will review for:**
1. Code quality and style
2. Test coverage
3. Documentation completeness
4. Safety considerations
5. Legal compliance
6. Overall project fit

**Possible outcomes:**
- **Approved**: Merged with thanks!
- **Changes Requested**: Feedback provided for improvements
- **Declined**: Explanation provided if not suitable

## Development Setup

### Environment Setup

```bash
# Clone repository
git clone https://github.com/A1Tman/rf-reverse-engineering.git
cd rf-reverse-engineering

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks (if available)
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gazco_rf --cov-report=html

# Run specific test file
pytest tests/test_controller.py

# Run with verbose output
pytest -v
```

### Code Quality Checks

```bash
# Format code with black
black .

# Check style with flake8
flake8 .

# Type checking with mypy
mypy src/

# Sort imports
isort .
```

## Questions?

**For questions about contributing:**
- Open a GitHub issue with `[Question]` prefix
- Check existing issues and discussions
- Review the methodology documentation

**For security concerns:**
- Email maintainer privately (see repository contact)
- Do not post publicly until coordinated disclosure

---

Thank you for contributing to RF reverse engineering education and research!

**License**: By contributing, you agree that your contributions will be licensed under the MIT License.

**Code of Conduct**: All contributors are expected to adhere to the standards outlined in this document.
