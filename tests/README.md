# Tests

This directory contains tests for the Clipboard Sync Tool.

## Structure

- **unit/** - Unit tests for individual components
  - `test_clipboard.py` - Basic clipboard monitoring tests

- **integration/** - Integration tests for system components
  - `test_pairing_server.py` - Local P2P pairing server tests
  - `test_simple_server.py` - HTTP server connectivity tests
  - `test_http_response.py` - HTTP response verification tests

## Running Tests

### All Tests
```bash
python -m pytest tests/
```

### Unit Tests Only
```bash
python -m pytest tests/unit/
```

### Integration Tests Only
```bash
python -m pytest tests/integration/
```

### Specific Test
```bash
python tests/integration/test_pairing_server.py
```

## Test Requirements

- Python 3.8+
- pytest
- All dependencies from requirements.txt

Install test dependencies:
```bash
pip install -r requirements.txt
pip install pytest
```
