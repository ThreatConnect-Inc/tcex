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
tcex/case_management/artifact.py                              137     19    86%   125, 151, 157, 167, 177, 201, 211, 230, 236, 247, 257, 263, 274, 284, 294, 316, 325, 334, 352
tcex/case_management/artifact_type.py                          50      1    98%   81
tcex/case_management/assignee.py                               83     30    64%   29-38, 68, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 142-144, 149-153, 189
tcex/case_management/case.py                                  178     29    84%   38-39, 146, 152, 160-164, 169, 175, 186, 206, 219, 232, 243, 254, 264, 274, 287, 300, 306, 312, 318, 329, 360, 378, 387, 396, 405, 432
tcex/case_management/case_management.py                       100     48    52%   58-71, 83-100, 104-121, 142, 147
tcex/case_management/common_case_management.py                243     48    80%   31-46, 51, 81, 172, 198, 201, 224-225, 238-243, 249, 275-277, 291-292, 310, 351-355, 368-369, 382-383, 407-409, 417-422
tcex/case_management/common_case_management_collection.py     163     48    71%   72-88, 92-96, 163, 167, 172, 192-194, 225-230, 252-255, 260, 265, 283, 288, 293, 298, 303, 308, 327-331, 337, 342
tcex/case_management/filter.py                                 30      3    90%   33, 43, 58
tcex/case_management/note.py                                  129     21    84%   47-51, 123, 134, 139, 163, 173, 194, 206, 217, 227, 237, 243, 254, 303, 312, 321, 366
tcex/case_management/tag.py                                    70      9    87%   41, 45, 100, 106, 126, 141, 168, 177, 195
tcex/case_management/task.py                                  169     30    82%   128, 134, 140, 146, 152-154, 164, 174, 189, 214, 224, 253, 259, 265, 271, 287, 297, 307, 317, 339, 348, 366, 375, 402, 411, 420, 447, 483, 492
tcex/case_management/tql.py                                   125     77    38%   32, 53-87, 109-114, 150-184
tcex/case_management/workflow_event.py                        109     14    87%   102, 107, 126, 136, 156, 166, 192, 198, 204, 215, 226, 267, 294, 303
tcex/case_management/workflow_template.py                      94     22    77%   39, 50, 119, 129, 154, 162-163, 173, 188, 201, 210, 219, 228, 237, 246, 255, 264, 273, 282, 291, 300, 309
-----------------------------------------------------------------------------------------
TOTAL                                                        1694    399    76%
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
