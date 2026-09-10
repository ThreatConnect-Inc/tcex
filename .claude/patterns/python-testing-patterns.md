# TcEx 4.0 — Testing Patterns (`python-test-engineer`)

House-style idioms that recur across the `tests/` suite. New tests must match these so they read like the
existing suite and stay deterministic under `pytest -n auto` (xdist). Each entry cites real files.

---

## 1. Parametrize style — **REQUIRED** (mandated standard)

**Every** `@pytest.mark.parametrize` must use the explicit, keyword form below — named `argnames` /
`argvalues`, every case wrapped in `pytest.param(...)` with a human-readable `id=`. Do **not** use the bare
inline-tuple form, positional args, or the comma-string-ids shortcut. A leading comment on each
`pytest.param` describing the case is encouraged.

```python
@pytest.mark.parametrize(
    argnames='key,ciphertext,iv,expected',
    argvalues=[
        pytest.param(
            # iv of None
            'ajfmuyodhscwegea',
            b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n',
            None,
            b'blah',
            id='pass-iv-none',
        ),
        pytest.param(
            # iv of bytes
            'ajfmuyodhscwegea',
            b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n',
            b'\0' * 16,
            b'blah',
            id='pass-iv-bytes',
        ),
        pytest.param(
            # iv of string
            'ajfmuyodhscwegea',
            b'0\x8e`\x8d%\x9f\x8c\xdf\x004\xc1\x1a\x82\xbd\x89\n',
            '\0' * 16,
            b'blah',
            id='pass-iv-string',
        ),
    ],
)
def test_decrypt_aes_cbc(self, key, ciphertext, iv, expected): ...
```

Rules:
- `argnames=` is a single comma-separated string; `argvalues=` is a list of `pytest.param(...)`.
- Every `pytest.param` ends with an explicit `id='...'` using lowercase, hyphenated, descriptive slugs
  (e.g. `pass-iv-none`, `fail-empty-value`). Prefix `pass-` / `fail-` when a suite mixes success and error
  cases.
- Positional values in `pytest.param` line up with `argnames` order.
- For expected-failure rows, attach the marker to the row: `pytest.param(..., marks=pytest.mark.xfail(reason='...'), id='...')`.

> Note: most existing tests predate this standard and still use inline tuples — do **not** treat those as the
> template. New and modified parametrized tests use the form above.

---

## 2. Fixtures + `MockApp` factory for building a configured `TcEx`

Tests obtain a configured `TcEx` through fixtures in `tests/conftest.py` (`tcex`, `tcex_hmac`,
`tcex_proxy`, `playbook_app`, `service_app`), which build instances via the `MockApp` helper
(`tests/mock_app.py`). The `playbook_app` / `service_app` fixtures are **callable factories** — call them
with config to get a fresh app, and read `.tcex` off the result. Prefer these over hand-constructing `TcEx`.

`tests/conftest.py`, `tests/mock_app.py`, `tests/app/playbook/test_playbook.py`.

```python
def test_x(self, playbook_app: Callable[..., MockApp]):
    tcex = playbook_app(config_data={'tc_playbook_out_variables': [...]}).tcex
    playbook = tcex.app.playbook
```

---

## 3. Reset cached/scoped/registry state between tests

Fresh-`TcEx` fixtures call `_reset_modules()` first, which clears the three project descriptors so cached
state never leaks across tests (critical under xdist). When a test class manages its own `TcEx`, reset the
same three in `setup_method`.

`tests/conftest.py:34` (`_reset_modules`).

```python
def _reset_modules():
    registry._reset()
    cached_property._reset()
    scoped_property._reset()
```

---

## 4. fakeredis instead of a live Redis

Redis-backed code is tested against `fakeredis` — never a real server. `conftest.py` swaps
`RedisClient.client` for a `fakeredis.FakeRedis()` globally in `pytest_configure`, and a `redis_client`
fixture returns one directly. Read/assert KV state through the normal client API.

`tests/conftest.py` (`pytest_configure`, `redis_client`).

```python
data = tcex.app.key_value_store.redis_client.hgetall(context)
```

---

## 5. `DeepDiff` for structural comparison

Compare nested dicts / serialized pydantic models with `deepdiff.DeepDiff(..., ignore_order=True)` and
assert the diff is empty with a message naming the subject. Use this instead of brittle field-by-field
equality for JSON-model validation.

`tests/app/config/test_tcex_json_model.py`, `tests/app/config/test_install_json_model.py`.

```python
ddiff = DeepDiff(
    expected,
    json.loads(model.json(by_alias=True, exclude_defaults=True, exclude_none=True)),
    ignore_order=True,
)
assert not ddiff, f'Failed validation of file {fqfn.name}'
```

---

## 6. Shared test base classes for a family of cases

A test family that repeats setup/validation logic factors it into a base class (e.g. `InputTest` in
`tests/input/field_type/util.py`) with `@staticmethod`/helper methods; concrete test classes subclass it.
Reuse the existing base for new field-type tests rather than re-deriving staging logic.

`tests/input/field_type/util.py` (`InputTest`), `tests/input/field_type/test_field_type_ip_address.py`.

---

## 7. `monkeypatch` + small mock response classes

Mock API/session behavior with `monkeypatch.setattr(...)`, returning lightweight mock classes that mimic the
real response surface (`.ok`, `.status_code`, `.json()`). Keep reusable mocks beside the tests
(e.g. `tests/.../mock_post.py`). Never hit a live network.

`tests/api/tc/v2/datastore/test_datastore.py`, `tests/api/tc/v2/datastore/mock_post.py`.

```python
def mp_post(*args, **kwargs):
    return MockPost({}, ok=False)


monkeypatch.setattr(tcex.session.tc, 'post', mp_post)
```

---

## 8. `caplog` for log assertions

Assert on emitted logs with the `caplog` fixture (`caplog.text`, `caplog.records`, `caplog.at_level(...)`)
rather than capturing stdout.

`tests/logger/test_logger.py`, `tests/logger/test_api_handler.py`.

```python
def test_logger_level(tcex: TcEx, caplog: pytest.LogCaptureFixture):
    assert 'DEBUG LOGGING' in caplog.text
    assert any(r.levelno == logging.DEBUG for r in caplog.records)
```

---

## 9. Isolation: `tmp_path` + autouse working-directory fixture

Every test runs in its own temp working directory via the `autouse` `change_test_dir` fixture
(keyed on `request.node.name`); tests that create files take `tmp_path` and build paths under it. Never
write to a shared/fixed path — it breaks parallel workers.

`tests/conftest.py` (`change_test_dir`), `tests/pleb/test_cached_property_filesystem.py`.

---

## 10. Assertion messages carry context

Equality assertions include an f-string message echoing actual vs expected so xdist failures are diagnosable
from the summary line alone.

```python
assert result == expected, f'Input {string} result of {result} != {expected}'
```

`tests/util/test_string_operation_to_bool.py`, `tests/app/playbook/test_playbook.py`.

---

## 11. `setup_class` for static data, `setup_method` for per-test reset; `@staticmethod` tests

Use `setup_class` for immutable shared test data and `setup_method` for per-test cleanup (resetting
scoped/cached/registry state). Test methods that need only fixtures (no `self` state) are written as
`@staticmethod`.

`tests/app/playbook/test_playbook.py`, `tests/api/tc/v2/batch/test_batch.py`,
`tests/requests_tc/test_session_tc.py`.

---

### Layout & determinism (always)
- Mirror the package: a test for `tcex/<area>/...` lives in `tests/<area>/...`; create the area dir if absent.
- ruff-clean + ruff-formatted (`tests/` is excluded from ty).
- No order dependence, no shared mutable globals, no real network/redis — xdist-safe by construction.
