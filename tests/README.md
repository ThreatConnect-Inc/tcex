# Test a specific module
pytest tests/batch

# Test a specific file
pytest tests/case_management/test_artifact_interface.py

# Test a specific test case in a file
pytest tests/case_management/test_artifact_interface.py::test_artifact_type_api_options

# Coverage Testing
pytest --cov=. --cov-report term-missing tests/

# Coverage on Single Module
pytest --cov=tcex/case_management/ --cov-report term-missing tests/case_management/
pytest --cov=tcex/utils/ --cov-report term-missing tests/utils/

# Release Testing Run
pytest --cov=. --cov-report html:tests/reports/cov-report --html=tests/reports/tcex-report.html --self-contained-html tests/

# Test Coverage (2020-01)

## case_management

```
Name                                                        Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------------------------
tcex/case_management/__init__.py                                2      0   100%
tcex/case_management/api_endpoints.py                          12      0   100%
tcex/case_management/artifact.py                              149      0   100%
tcex/case_management/artifact_type.py                          50      0   100%
tcex/case_management/assignee.py                               91      5    95%   33, 37, 68, 148, 205
tcex/case_management/case.py                                  192      4    98%   161, 234, 311, 320
tcex/case_management/case_management.py                        65      1    98%   59
tcex/case_management/common_case_management.py                207      6    97%   43, 68, 82, 207, 246-247
tcex/case_management/common_case_management_collection.py     136      8    94%   196, 276-279, 289, 315, 320
tcex/case_management/filter.py                                 25      0   100%
tcex/case_management/note.py                                  132      0   100%
tcex/case_management/tag.py                                    71      0   100%
tcex/case_management/task.py                                  181      3    98%   366, 384, 393
tcex/case_management/tql.py                                    47      0   100%
tcex/case_management/workflow_event.py                        105      3    97%   210-214
tcex/case_management/workflow_template.py                      71      2    97%   211, 220
-----------------------------------------------------------------------------------------
TOTAL                                                        1536     32    98%
```

## datastore

```
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
tcex/datastore/__init__.py        3      0   100%
tcex/datastore/cache.py          50     10    80%   61-62, 113-115, 119-124
tcex/datastore/datastore.py      92      0   100%
-----------------------------------------------------------
TOTAL                           145     10    93%
```

## decorators

```
Name                                Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
tcex/decorators/__init__.py             2      0   100%
tcex/decorators/app_decorators.py     184     52    72%   317, 340, 478, 490-506, 537-540, 552-587, 623-626, 638-657
-----------------------------------------------------------------
TOTAL                                 186     52    72%
```

## inputs

```
Name                             Stmts   Miss  Cover   Missing
--------------------------------------------------------------
tcex/inputs/__init__.py              3      0   100%
tcex/inputs/argument_parser.py     103      0   100%
tcex/inputs/file_params.py          47      0   100%
tcex/inputs/inputs.py              131      0   100%
--------------------------------------------------------------
TOTAL                              284      0   100%
```

## logger

```
Name                                          Stmts   Miss  Cover   Missing
---------------------------------------------------------------------------
tcex/logger/__init__.py                           3      0   100%
tcex/logger/api_handler.py                       30      0   100%
tcex/logger/cache_handler.py                     14      0   100%
tcex/logger/logger.py                           111      0   100%
tcex/logger/rotating_file_handler_custom.py       8      0   100%
tcex/logger/thread_file_handler.py               10      0   100%
tcex/logger/trace_logger.py                      17      0   100%
---------------------------------------------------------------------------
TOTAL                                           193      0   100%
```

## metrics

```
Name                       Stmts   Miss  Cover   Missing
--------------------------------------------------------
tcex/metrics/__init__.py       2      0   100%
tcex/metrics/metrics.py       53      0   100%
--------------------------------------------------------
TOTAL                         55      0   100%
```

## notifications

```
Name                                  Stmts   Miss  Cover   Missing
-------------------------------------------------------------------
tcex/notifications/__init__.py            2      0   100%
tcex/notifications/notifications.py      28      0   100%
-------------------------------------------------------------------
TOTAL                                    30      0   100%
```

## playbooks

???

## sessions

```
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
tcex/sessions/__init__.py         2      0   100%
tcex/sessions/tc_session.py      63      0   100%
-----------------------------------------------------------
TOTAL                            65      0   100%
```

## ti

???

## tokens

```
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
tcex/tokens/__init__.py       2      0   100%
tcex/tokens/tokens.py       103      0   100%
-------------------------------------------------------
TOTAL                       105      0   100%
```

## utils

```
Name                       Stmts   Miss  Cover   Missing
--------------------------------------------------------
tcex/utils/__init__.py         2      0   100%
tcex/utils/date_utils.py      87      0   100%
tcex/utils/utils.py           41      0   100%
--------------------------------------------------------
TOTAL                        130      0   100%
```

# Case Management Error Codes

"""
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
"""
