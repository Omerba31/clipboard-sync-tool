# Tests

This directory contains tests for the Clipboard Sync Tool.

## Structure

- **unit/** - Unit tests for individual components
  - `test_clipboard.py` - Clipboard monitoring and dependency tests
  - `test_encryption.py` - E2E encryption tests (AES-256-GCM)
  - `test_crypto_compatibility.py` - Python ↔ JavaScript encryption compatibility
  - `test_sync_engine.py` - Sync engine functionality tests

- **integration/** - Integration tests for system components
  - `test_pairing_server.py` - Local P2P pairing server tests
  - `test_simple_server.py` - HTTP server and threading tests
  - `test_http_response.py` - HTTP connectivity and JSON handling tests
  - `test_cloud_relay_live.py` - Live cloud relay tests (connects to Railway)

## Running Tests

> **Note:** pytest is automatically installed when you run `.\scripts\install.ps1` or `pip install -r requirements.txt`

> **Windows Users:** Always use `python -m pytest` instead of `pytest` directly. Running `pytest` directly may fail with "Access is denied" due to Windows permissions issues.

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Unit Tests Only
```bash
python -m pytest tests/unit/ -v
```

### Run Integration Tests Only
```bash
python -m pytest tests/integration/ -v
```

### Run Specific Test File
```bash
python -m pytest tests/unit/test_encryption.py -v
```

### Run Specific Test Class
```bash
python -m pytest tests/unit/test_encryption.py::TestCloudRelayCrypto -v
```

### Run Specific Test Method
```bash
python -m pytest tests/unit/test_encryption.py::TestCloudRelayCrypto::test_encrypt_decrypt -v
```

### Run with Coverage
```bash
python -m pytest tests/ -v --cov=core --cov=gui
```

## Test Categories

### Unit Tests (`tests/unit/`)

| Test File | Description |
|-----------|-------------|
| `test_clipboard.py` | Tests for clipboard monitoring, dependencies |
| `test_encryption.py` | Tests for AES-256-GCM encryption, key derivation |
| `test_crypto_compatibility.py` | Tests Python ↔ JavaScript encryption compatibility |
| `test_sync_engine.py` | Tests for sync engine, settings, QR pairing |

### Integration Tests (`tests/integration/`)

| Test File | Description |
|-----------|-------------|
| `test_pairing_server.py` | Tests pairing server start/stop, URL generation |
| `test_simple_server.py` | Tests HTTP server, threading, client requests |
| `test_http_response.py` | Tests URL parsing, JSON handling, network helpers |
| `test_cloud_relay_live.py` | **LIVE** - Tests Railway server health, Socket.IO, message relay |

### Live Tests

The `test_cloud_relay_live.py` tests connect to the actual Railway server. These require internet and a running deployment.

```bash
# Run only live tests
python -m pytest tests/integration/test_cloud_relay_live.py -v

# Run all tests EXCEPT live tests (offline)
python -m pytest tests/ -v --ignore=tests/integration/test_cloud_relay_live.py
```

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

- Python 3.10+
- pytest (auto-installed with `pip install -r requirements.txt`)
- All dependencies from requirements.txt
