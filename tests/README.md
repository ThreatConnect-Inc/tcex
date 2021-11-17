# General Test Command

## Code Stats
```bash
find tcex/api/tc/v3 -type f | xargs wc -l
```

## Test a specific module
pytest tests/batch

## Test a specific file
pytest tests/case_management/test_artifact_interface.py

## Test a specific test case in a file
pytest tests/case_management/test_artifact_interface.py::test_artifact_type_api_options

## Coverage Testing
```bash
pytest -n 12 --cov=. --cov-report=term-missing tests/
```

```bash
> pytest --ignore-glob='*tokens*' --cov=tcex/ --cov-report=term-missing tests
> 2 failed, 871 passed, 28 warnings in 728.86s (0:12:08)
```

```bash
> pytest -n 12 --ignore-glob='*tokens*' --cov=tcex/ --cov-report=term-missing tests
> 4 failed, 869 passed, 28 warnings in 105.62s (0:01:45)`
```

```bash
> pytest -n 12 --cov=tcex/ --cov-report=term-missing tests
> 5 failed, 875 passed, 28 warnings in 105.23s (0:01:45)
```

# Module Testing

## api/tc

### v2

```bash
pytest --cov=tcex/api/tc/v2/ --cov-report=term-missing tests/api/tc/v2/
```

#### datastore

#### metrics

#### notification

#### threat_intelligence

### v3

```bash
pytest --cov=tcex/api/tc/v3/ --cov-report=term-missing tests/api/tc/v3/
```

#### artifact_types
```bash
pytest --cov=tcex/api/tc/v3/artifact_types --cov-report=term-missing tests/api/tc/v3/
```

#### attribute_types
```bash
pytest --cov=tcex/api/tc/v3/attribute_types --cov-report=term-missing tests/api/tc/v3/
```

#### artifacts
```bash
pytest --cov=tcex/api/tc/v3/artifacts --cov-report=term-missing tests/api/tc/v3/artifacts/
```

#### groups
```bash
pytest --cov=tcex/api/tc/v3/groups --cov-report=term-missing tests/api/tc/v3/groups/
```

#### indicators
```bash
pytest --cov=tcex/api/tc/v3/indicators --cov-report=term-missing tests/api/tc/v3/indicators/
```

#### notes
```bash
pytest --cov=tcex/api/tc/v3/notes --cov-report=term-missing tests/api/tc/v3/notes/
```

#### security -> owner_roles
```bash
pytest --cov=tcex/api/tc/v3/security/owner_roles --cov-report=term-missing tests/api/tc/v3/security/owner_roles
```

#### security -> owners
```bash
pytest --cov=tcex/api/tc/v3/security/owners --cov-report=term-missing tests/api/tc/v3/security/owners
```

#### security -> system_roles
```bash
pytest --cov=tcex/api/tc/v3/security/system_roles --cov-report=term-missing tests/api/tc/v3/security/system_roles
```

#### security -> user_groups
```bash
pytest --cov=tcex/api/tc/v3/security/user_groups --cov-report=term-missing tests/api/tc/v3/security/user_groups
```

#### security -> users
```bash
pytest --cov=tcex/api/tc/v3/security/users --cov-report=term-missing tests/api/tc/v3/security/users
```

#### tasks
```bash
pytest --cov=tcex/api/tc/v3/tasks --cov-report=term-missing tests/api/tc/v3/tasks/
```

## app_config
```bash
pytest --cov=tcex/app_config/ --cov-report=term-missing tests/app_config/
```

## app_feature
```bash
pytest --cov=tcex/app_feature/ --cov-report=term-missing tests/app_feature/
```

## input
```bash
pytest --cov=tcex/input/ --cov-report=term-missing tests/input/
```
