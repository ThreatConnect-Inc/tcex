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

# Coverage on Single Module
pytest -n 12 --cov=tcex/batch/ --cov-report=term-missing tests/batch/
pytest -n 12 --cov=tcex/case_management/ --cov-report=term-missing tests/case_management/
pytest -n 12 --cov=tcex/datastore/ --cov-report=term-missing tests/datastore/
pytest -n 12 --cov=tcex/decorators/ --cov-report=term-missing tests/decorators/
pytest -n 12 --cov=tcex/inputs/ --cov-report=term-missing tests/inputs/
pytest -n 12 --cov=tcex/logger/ --cov-report=term-missing tests/logger/
pytest -n 12 --cov=tcex/metrics/ --cov-report=term-missing tests/metrics/
pytest -n 12 --cov=tcex/playbooks/ --cov-report=term-missing tests/playbooks/
pytest -n 12 --cov=tcex/sessions/ --cov-report=term-missing tests/sessions/
pytest -n 12 --cov=tcex/ --cov-report=term-missing tests/tcex_methods/
pytest -n 12 --cov=tcex/threat_intelligence/ --cov-report=term-missing tests/threat_intelligence/
pytest -n 12 --cov=tcex/tokens/ --cov-report=term-missing tests/tokens/
pytest -n 12 --cov=tcex/utils/ --cov-report=term-missing tests/utils/

# Release Testing Run
# normal - in 1526.29s
pytest --cov=. --cov-report=term-missing --cov-report=html:tests/reports/cov-report --html=tests/reports/tcex-report.html --self-contained-html tests/
# concurrent normal - in 170.33s (0:02:50)
pytest -n 12 --cov=. --cov-report=term-missing --cov-report=html:tests/reports/cov-report --html=tests/reports/tcex-report.html --self-contained-html tests/
# concurrent loadscope - in 196.37s (0:03:16)
pytest -n 12 --dist=loadscope --cov=. --cov-report=term-missing --cov-report=html:tests/reports/cov-report --html=tests/reports/tcex-report.html --self-contained-html tests/
# concurrent loadfile - in 210.22s (0:03:30)
pytest -n 12 --dist=loadfile --cov=. --cov-report=term-missing --cov-report=html:tests/reports/cov-report --html=tests/reports/tcex-report.html --self-contained-html tests/

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
