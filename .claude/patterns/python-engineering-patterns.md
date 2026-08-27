# TcEx 4.0 — Engineering Patterns (`python-engineer`)

House-style idioms that recur across the TcEx framework. When you add or modify framework code,
match the relevant pattern below so the change is indistinguishable from the surrounding code.
These are **observed, enforced conventions** — not generic advice. Each entry cites real files.

> Scope note: generated V3 code (`tcex/api/tc/v3/**` `*_model.py`/`*_filter.py`/object files) is owned
> by the generator in `tcex/api/tc/v3/_gen/`. Patterns that appear in generated output are changed by
> editing the generator, never the output (see CLAUDE.md + the agent file).

---

## 1. Module-level logger via the top-level package name

Every module that logs binds a module-scoped `_logger` by splitting `__name__` on the first dot, so all
records route through the single `tcex` logger hierarchy (and the custom `TraceLogger`). Do **not** call
`logging.getLogger(__name__)` (full dotted path) — always the top-level segment.

Pervasive: ~49 modules (`requests_tc/requests_tc.py:17`, `app/token/token.py:22`,
`app/playbook/playbook.py:15`, `input/field_type/exception.py`).

```python
# standard library
import logging

# first-party
from tcex.logger.trace_logger import TraceLogger

_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore
```

Use the bare `_logger = logging.getLogger(__name__.split('.', maxsplit=1)[0])` form when the `TraceLogger`
annotation/`trace()` calls are not needed; add the annotated form (with `# type: ignore`) when the module
calls `_logger.trace(...)`.

---

## 2. Lazy attributes: `cached_property` vs `scoped_property` (from `tcex.pleb`)

Two project-specific descriptors back almost all lazily-built attributes. **Pick by lifetime**, and always
import from `tcex.pleb` (not `functools`) so the test suite's `_reset()` can clear them between tests.

- `from tcex.pleb.cached_property import cached_property` — compute once per instance, cache for the
  instance's life. Use for inputs-derived helpers, sub-APIs, parsed files. (~18 modules: `tcex/tcex.py`,
  `app/app.py`, `app/playbook/playbook.py`.)
- `from tcex.pleb.scoped_property import scoped_property` — thread/process-aware caching that detects
  process forking; use for per-execution resources that must not leak across threads/forks (session,
  KV store). (`tcex/tcex.py`, `app/app.py`, `requests_tc/requests_tc.py`.)

```python
from tcex.pleb.cached_property import cached_property


@cached_property
def api(self) -> API:
    """Return instance of API."""
    return API(self.inputs, self.session.tc)
```

> The shared `registry` (`tcex/registry.py`) is a dependency-injection primitive used at the very top of
> the object graph (`tcex/tcex.py`). It is **not** a routine pattern — only wire into it when extending the
> top-level `TcEx` composition, and follow the single existing `@registry.factory(...)` example exactly.

---

## 3. pydantic **v1** model `Config` conventions

Config-/install-json-facing models share a consistent inner `Config`: a `snake_to_camel` alias generator
(Python snake_case attrs ↔ camelCase JSON), `validate_assignment = True`, and an explicit `Extra` policy.
Match the **same `Extra`** the neighboring models use (`allow` for install.json passthrough, `forbid`/`ignore`
where the surface is closed).

`app/config/model/install_json_model.py`, `app/config/model/layout_json_model.py`, `input/input.py`.

```python
from pydantic import BaseModel, Extra
from tcex.util.string_operation import snake_to_camel


class Config:
    """DataModel Config"""

    alias_generator = snake_to_camel
    validate_assignment = True
    extra = Extra.allow
```

When serializing v1 models, use the v1 kwargs the codebase relies on:
`model.json(by_alias=True, exclude_defaults=True, exclude_none=True)` / `.dict(by_alias=True)`.

---

## 4. Custom field types: `__get_validators__` chain + `pre`/`always` validators

Input field types subclass a builtin (`str`, etc.) and expose a validator **chain** from
`__get_validators__`, each step a `@classmethod (cls, value, field: ModelField) -> value` that raises a
custom exception on failure and otherwise returns the (possibly transformed) value. Order matters — type
check first, then transforms, then constraint checks.

`input/field_type/string.py`, `input/field_type/sensitive.py`, `input/field_type/binary.py`.

```python
class String(str):
    allow_empty: bool = True
    max_length: int | None = None

    @classmethod
    def __get_validators__(cls) -> Generator:
        yield cls.validate_type
        yield cls.validate_strip
        yield cls.validate_allow_empty
        yield cls.validate_max_length

    @classmethod
    def validate_allow_empty(cls, value: str, field: ModelField) -> str:
        if cls.allow_empty is False and isinstance(value, str) and value == '':
            raise InvalidEmptyValue(field_name=field.name)
        return value
```

### 4a. Constrained-type factory (`type(...)` subclass)

Pair each field type with a lowercase factory that returns a **configured subclass** via `type('ConstrainedX', (X,), namespace)` — this is how constraints are composed without a new class per combination.

```python
def string(allow_empty: bool = True, max_length: int | None = None, ...) -> type[String]:
    """Return configured instance of String."""
    namespace = {'allow_empty': allow_empty, 'max_length': max_length, ...}
    return type('ConstrainedString', (String,), namespace)
```

### 4b. Reusable validators are higher-order closures

Cross-field validators are factory functions returning a closure used with `@validator(..., pre=True)` /
`always=True`. See `always_array(...)` in `input/field_type/validator.py`.

---

## 5. Custom exception hierarchy with `field_name` + trace logging

Validation/runtime errors subclass a small base that **logs on construction** and carries a `field_name`
for tracing which field failed. Subclasses only build the message. Raise these (never bare `ValueError`)
from field validators.

`input/field_type/exception.py`.

```python
class BaseValueError(ValueError):
    def __init__(self, field_name: str, message: str):
        _logger.trace(f'Checking value for field {field_name}: {message}')
        super().__init__(message)


class InvalidEmptyValue(BaseValueError):
    def __init__(self, field_name: str):
        super().__init__(field_name, 'an empty value is not allowed for this field')
```

---

## 6. Self-referential models: `update_forward_refs()`

Recursive models declare the forward ref and call `update_forward_refs()` at module bottom (v1 requirement).
Do this for any model that references itself or a not-yet-defined sibling.

`input/field_type/key_value.py`, `app/config/model/layout_json_model.py`.

```python
KeyValue = ForwardRef('KeyValue')


class KeyValue(BaseModel):
    key: str
    value: 'list[KeyValue] | KeyValue | str | None'


KeyValue.update_forward_refs()
```

---

## 7. Composed input models via mixins + `input_model()` factory

The runtime input model is assembled from focused mixin models (`ApiModel`, `BatchModel`, `LoggingModel`,
`ProxyModel`, …) into umbrella models (`CommonModel`, `CommonAdvancedModel`), then finalized by the
`input_model(models)` factory that dynamically subclasses them and adds the common `tc_*` fields. Add new
input surface as a focused mixin and compose it — do not bolt fields onto an umbrella model directly.

`input/model/common_model.py`, `input/model/api_model.py`, `input/input.py`.

```python
class CommonModel(ApiModel, BatchModel, CertModel, LoggingModel, PathModel, ProxyModel):
    """Model Definition"""
```

---

## 8. Interface via ABC + runtime implementation selection

Pluggable subsystems define an `ABC` with `@abstractmethod`s, and a holder picks the concrete
implementation at runtime behind a `cached_property` (redis / api / mock). Add a new backend by
implementing the ABC and extending the selector — keep the public method surface identical to the ABC.

`app/key_value_store/key_value_abc.py`, `app/key_value_store/key_value_store.py`.

```python
class KeyValueABC(ABC):
    @abstractmethod
    def create(self, context: str, key: str, value: Any) -> int: ...


class KeyValueStore:
    @cached_property
    def client(self) -> KeyValueApi | KeyValueMock | KeyValueRedis:
        if self.tc_kvstore_type == 'Redis':
            return KeyValueRedis(self.redis_client)
        ...
```

---

## 9. Conditional/late imports for heavy or app-type-specific modules

Branch-selected heavy modules (services) are imported **inside** the property that needs them, with
`# noqa: PLC0415`, to avoid hard import-time dependencies. Use this only for genuinely conditional/heavy
imports — normal imports stay at module top, isort-ordered into `# standard library` / `# third-party` /
`# first-party` blocks.

`app/app.py` (`service` property).

```python
@cached_property
def service(self) -> 'ApiService | CommonServiceTrigger | WebhookTriggerService':
    if self.install_json.model.is_api_service_app:
        from tcex.app.service import ApiService as Service  # noqa: PLC0415
    ...
```

---

## 10. V3 generator structure (when touching `tcex/api/tc/v3/_gen/`)

The generator is the hand-written source for all generated V3 code. It is organized as ABC base classes
(`GenerateABC`, `GenerateModelABC`, `GenerateObjectABC`, …) that carry a `self.requirements` import map
(`'standard library' / 'third-party' / 'first-party'`) and emit code from per-type subclasses. To change
generated output, change the emitting method here, then regenerate and run `pre-commit run --all-files`
(generator output is post-formatted by ruff/isort — that combination is the committed state).

`api/tc/v3/_gen/_gen_model_abc.py`, `api/tc/v3/_gen/_gen_object_abc.py`, `api/tc/v3/_gen/_gen_abc.py`.

---

### Import-block convention (applies everywhere)

Imports are grouped and commented in three isort sections; keep the comments:

```python
# standard library
import logging

# third-party
from pydantic import BaseModel

# first-party
from tcex.pleb.cached_property import cached_property
```
