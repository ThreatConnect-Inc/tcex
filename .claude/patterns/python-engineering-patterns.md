# TcEx 5.0 — Engineering Patterns (`python-engineer`)

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

## 3. pydantic **v2** `model_config` conventions

Config-/install-json-facing models share a consistent `model_config = ConfigDict(...)`: a `to_camel`
alias generator (Python snake_case attrs ↔ camelCase JSON), `validate_assignment=True`, and an explicit
`extra` policy. Match the **same `extra`** the neighboring models use (`'allow'` for install.json
passthrough, `'forbid'`/`'ignore'` where the surface is closed). Note the alias generator is `to_camel`
from `pydantic.alias_generators` (not the old custom `snake_to_camel`), and `extra` is a **string**
(`'allow'`/`'ignore'`/`'forbid'`), not the removed `Extra` enum.

`app/config/model/install_json_model.py`, `app/config/model/layout_json_model.py`, `input/input.py`.

```python
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class InstallJsonModel(BaseModel):
    """Install.json data model."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_assignment=True,
        extra='allow',
    )
```

A subclass can override a single config knob inline via class kwargs (e.g.
`class _PathModel(PathModel, extra='ignore'): ...`).

When serializing v2 models, use the v2 methods the codebase relies on:
`model.model_dump_json(by_alias=True, exclude_defaults=True, exclude_none=True)` /
`model.model_dump(by_alias=True)` — not the removed `.json()` / `.dict()`.

---

## 4. Custom field types: `__get_pydantic_core_schema__` + a single `_validate` chain

Input field types subclass a builtin (`str`, etc.) and implement pydantic-v2's
`__get_pydantic_core_schema__`, returning a `core_schema.with_info_after_validator_function(...)` that
wraps the appropriate base schema (`core_schema.str_schema(...)`) and runs a single `_validate`
classmethod. `_validate(cls, value, info: core_schema.ValidationInfo)` reads `info.field_name` and calls
the per-step `@classmethod (cls, value, field_name: str) -> value` validators **in order** — type check
first, then transforms, then constraint checks — each raising a custom exception on failure. Class-level
constraints are `ClassVar`s. (This replaces the removed v1 `__get_validators__` + `ModelField` chain.)

`input/field_type/string.py`, `input/field_type/sensitive.py`, `input/field_type/binary.py`.

```python
from typing import Any, ClassVar

from pydantic.annotated_handlers import GetCoreSchemaHandler
from pydantic_core import core_schema


class String(str):
    allow_empty: ClassVar[bool] = True
    max_length: ClassVar[int | None] = None
    min_length: ClassVar[int | None] = None

    @classmethod
    def _validate(cls, value: str, info: core_schema.ValidationInfo) -> str:
        field_name = info.field_name or '--unknown--'
        value = cls.validate_type(value, field_name)
        value = cls.validate_strip(value)
        value = cls.validate_allow_empty(value, field_name)
        return value

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.AfterValidatorFunctionSchema:
        return core_schema.with_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(max_length=cls.max_length, min_length=cls.min_length),
            field_name=handler.field_name,
        )

    @classmethod
    def validate_allow_empty(cls, value: str, field_name: str) -> str:
        if cls.allow_empty is False and value in (b'', ''):
            raise InvalidEmptyValue(field_name)
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

Cross-field validators are factory functions returning a closure registered with
`@field_validator(..., mode='before')` (or `mode='after'`). The closure takes
`(value, info: ValidationInfo)` — `ValidationInfo` and `field_validator` import from `pydantic`. See
`always_array(...)` and `conditional_required(...)` in `input/field_type/validator.py`.

```python
from pydantic import ValidationInfo, field_validator

def always_array(allow_empty: bool = True, ...) -> Callable:
    """Return a customized validator that always returns a list."""
    def _always_array(value: Any, info: ValidationInfo) -> list[Any]:
        ...
        return value
    return _always_array
```

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

## 6. Self-referential models: `model_rebuild()`

Recursive models declare the forward ref and call `model_rebuild()` at module bottom (the v2 replacement
for v1's `update_forward_refs()`). Do this for any model that references itself or a not-yet-defined
sibling.

`input/field_type/key_value.py`, `app/config/model/layout_json_model.py`.

```python
from typing import ForwardRef

KeyValue = ForwardRef('KeyValue')  # type: ignore


class KeyValue(BaseModel):
    key: str
    value: 'list[KeyValue] | KeyValue | str | None'


KeyValue.model_rebuild()
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
