# Test a specific module
pytest tests/batch

# Test a specific file
pytest tests/case_management/test_artifact_interface.py

# Test a specific test case in a file
pytest tests/case_management/test_artifact_interface.py::test_artifact_type_api_options

# Coverage Testing
pytest -n 12 --cov=. --cov-report=term-missing tests/

pytest --ignore-glob='*tokens*' --cov=tcex/ --cov-report=term-missing tests
# 2 failed, 871 passed, 28 warnings in 728.86s (0:12:08)

pytest -n 12 --ignore-glob='*tokens*' --cov=tcex/ --cov-report=term-missing tests
# 4 failed, 869 passed, 28 warnings in 105.62s (0:01:45)

pytest -n 12 --cov=tcex/ --cov-report=term-missing tests
# 5 failed, 875 passed, 28 warnings in 105.23s (0:01:45)

# Module Testing

## api/tc

### v2

### v3

pytest --cov=tcex/api/tc/v3/ --cov-report=term-missing tests/api/tc/v3/

#### artifact_types
pytest --cov=tcex/api/tc/v3/artifact_types --cov-report=term-missing tests/api/tc/v3/artifact_types/test_artifact_type_interface.py

#### artifacts
pytest --cov=tcex/api/tc/v3/artifacts --cov-report=term-missing tests/api/tc/v3/artifacts/test_artifact_interface.py

#### notes
pytest --cov=tcex/api/tc/v3/notes --cov-report=term-missing tests/api/tc/v3/notes/test_note_interface.py

#### tasks
pytest --cov=tcex/api/tc/v3/tasks --cov-report=term-missing tests/api/tc/v3/tasks/test_task_interface.py

## app_config

pytest --cov=tcex/app_config/ --cov-report=term-missing tests/app_config/

## app_feature

pytest --cov=tcex/app_feature/ --cov-report=term-missing tests/app_feature/

## input

pytest --cov=tcex/input/ --cov-report=term-missing tests/input/

# Case Management Error Codes

```
/v3/ Error Codes:

Error Code Name   Ref Code  Code  Default Text
BadRequest        0x1001    400   An unspecified issue exists with your request. Check your request
                                  and try again.
Unauthorized      0x1002    401   You are not authorized to perform the requested operation.
Forbidden         0x1003    403   You do not have permission to perform the requested operation.
NotFound          0x1004    404   The requested item(s) were not found.
MethodNotAllowed  0x1005    405   This operation is not supported.
Conflict          0x1006    409   An item already exists with the same unique information.
InternalError     0x1007    500   An internal error occurred while processing your request. If the
                                  problem persists contact your system administrator.
TqlParseError     0x2001    400   Syntax error(s) found with your TQL query. Check your query and
                                  try again.
MismatchedItems   0x2002    400   Your request could not be processed because it references items
                                  that cannot belong together.
MissingData       0x2003    400   Your request was missing required data and could not be processed.
PlaybookFailure   0x2004    400   An automated task could not run based on your request.
ImproperFormat    0x2005    400   The request does not match the expected format.
HasDependents     0x2006    400   The request cannot be completed because the item is referenced by
```
