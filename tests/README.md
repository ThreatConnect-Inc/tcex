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
tcex/case_management/artifact.py                              146     28    81%   126, 152, 158, 168, 178, 202, 212, 231, 237, 248, 258, 264, 275, 285, 295, 313-317, 322-326, 331-335, 353
tcex/case_management/artifact_type.py                          50      1    98%   81
tcex/case_management/assignee.py                               83     29    65%   29-38, 68, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 130, 142-144, 149-153, 189
tcex/case_management/case.py                                  190     40    79%   39, 146, 152, 160-164, 169, 175, 186, 206, 219, 232, 243, 254, 264, 274, 287, 300, 306, 312, 318, 329, 360, 374-378, 383-387, 392-396, 401-405, 432
tcex/case_management/case_management.py                       100     47    53%   58-71, 83-100, 104-121, 147
tcex/case_management/common_case_management.py                249     50    80%   31-44, 49, 67, 81, 172, 198, 201, 224-225, 239, 241-246, 252, 278-280, 294-295, 309, 316, 357-361, 374-375, 389, 392-393, 417-419, 427-432
tcex/case_management/common_case_management_collection.py     173     35    80%   78, 92-96, 220, 224, 229, 249-251, 282-287, 309-312, 317, 322, 340, 345, 350, 355, 360, 365, 384-388, 394, 399
tcex/case_management/filter.py                                 31      3    90%   34, 44, 59
tcex/case_management/note.py                                  138     30    78%   47-51, 123, 134, 139, 163, 173, 194, 206, 217, 227, 237, 243, 254, 299-303, 308-312, 317-321, 366
tcex/case_management/tag.py                                    73     12    84%   41, 45, 100, 106, 126, 141, 168, 173-177, 195
tcex/case_management/task.py                                  182     22    88%   146, 159, 273, 347, 356, 374, 383, 406-410, 415-419, 424-428, 455, 491, 500
tcex/case_management/tql.py                                   132     81    39%   33, 54-88, 111, 113-122, 163-197
tcex/case_management/workflow_event.py                        104      2    98%   201, 298
tcex/case_management/workflow_template.py                      80      2    98%   294, 304
-----------------------------------------------------------------------------------------
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
