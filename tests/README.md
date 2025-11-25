# Tests

This directory contains tests for the Clipboard Sync Tool.

## Structure

- **unit/** - Unit tests for individual components
  - `test_clipboard.py` - Clipboard monitoring and dependency tests
  - `test_encryption.py` - E2E encryption tests (AES-256-GCM)
  - `test_sync_engine.py` - Sync engine functionality tests

- **integration/** - Integration tests for system components
  - `test_pairing_server.py` - Local P2P pairing server tests
  - `test_simple_server.py` - HTTP server and threading tests
  - `test_http_response.py` - HTTP connectivity and JSON handling tests

## Running Tests

> **Note:** pytest is automatically installed when you run `.\scripts\install.ps1` or `pip install -r requirements.txt`

### Run All Tests
```bash
pytest tests/ -v
```

### Run Unit Tests Only
```bash
pytest tests/unit/ -v
```

### Run Integration Tests Only
```bash
pytest tests/integration/ -v
```

### Run Specific Test File
```bash
pytest tests/unit/test_encryption.py -v
```

### Run Specific Test Class
```bash
pytest tests/unit/test_encryption.py::TestCloudRelayCrypto -v
```

### Run Specific Test Method
```bash
pytest tests/unit/test_encryption.py::TestCloudRelayCrypto::test_encrypt_decrypt -v
```

### Run with Coverage
```bash
pytest tests/ -v --cov=core --cov=gui
```

## Test Categories

### Unit Tests (`tests/unit/`)

| Test File | Description |
|-----------|-------------|
| `test_clipboard.py` | Tests for clipboard monitoring, dependencies |
| `test_encryption.py` | Tests for AES-256-GCM encryption, key derivation |
| `test_sync_engine.py` | Tests for sync engine, settings, QR pairing |

### Integration Tests (`tests/integration/`)

| Test File | Description |
|-----------|-------------|
| `test_pairing_server.py` | Tests pairing server start/stop, URL generation |
| `test_simple_server.py` | Tests HTTP server, threading, client requests |
| `test_http_response.py` | Tests URL parsing, JSON handling, network helpers |

## Writing New Tests

Use pytest conventions:
- Test files should start with `test_`
- Test classes should start with `Test`
- Test methods should start with `test_`
- Use fixtures for shared setup/teardown

Example:
```python
import pytest

class TestMyFeature:
    @pytest.fixture
    def my_fixture(self):
        return SomeObject()
    
    def test_something(self, my_fixture):
        assert my_fixture.method() == expected
```

## Test Requirements

- Python 3.8+
- pytest
- All dependencies from requirements.txt
