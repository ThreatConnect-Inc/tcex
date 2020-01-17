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
tcex/case_management/artifact.py                              149     16    89%   241-245, 327-331, 336-340, 345-349, 367
tcex/case_management/artifact_type.py                          50      1    98%   81
tcex/case_management/assignee.py                               91     24    74%   29-38, 68, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 130, 148, 160, 205
tcex/case_management/case.py                                  192     24    88%   161, 206, 243, 314, 320, 331, 362, 376-380, 385-389, 394-398, 403-407, 434
tcex/case_management/case_management.py                       100     46    54%   58-71, 83-100, 104-121
tcex/case_management/common_case_management.py                249     47    81%   31-44, 49, 67, 81, 175, 204, 227-228, 242, 244-249, 255, 281-283, 297-298, 312, 319, 360-364, 392, 395-396, 420-422, 430-435
tcex/case_management/common_case_management_collection.py     169     32    81%   88-92, 216, 220, 225, 278-283, 305-308, 313, 318, 331, 336, 341, 346, 351, 356, 361, 380-384, 390, 395
tcex/case_management/filter.py                                 31      3    90%   34, 44, 59
tcex/case_management/note.py                                  138     29    79%   47-51, 123, 134, 139, 163, 173, 194, 206, 217, 227, 243, 254, 299-303, 308-312, 317-321, 366
tcex/case_management/tag.py                                    73      2    97%   41, 45
tcex/case_management/task.py                                  181      3    98%   366, 384, 393
tcex/case_management/tql.py                                   132     80    39%   33, 54-88, 113-122, 163-197
tcex/case_management/workflow_event.py                        107      4    96%   210-214, 311
tcex/case_management/workflow_template.py                      74      2    97%   278, 287
-----------------------------------------------------------------------------------------
TOTAL                                                        1750    313    82%
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

# Issues:


## Artifact


## Artifact Type


## Case


## Note


## Tag


## Common Case Management Collection

* @bpurdy - [line 387-395] - remove retry logic from get and other methods
* @bpurdy - [line 300-305] - is list_as_dict() method needed?


## TQL
* @bpurdy - [line 33] supported dict checking if needed
* @bpurdy - [line 54-88] operator.get checking if needed
* @bpurdy - [line 163-197] type.get_operator checking if needed
* @bpurdy - difference between get and get_operator

## Tasks

* @mj - can completedBy be set via the API?
* @mj - bug when adding artifact to task gets added to case.
* @mj - how to add configTask via API?
* @mj - TQL keyword configPlaybook valid?
* @mj - TQL keyword configTask valid?


## Workflow Event

* @mj - are we still supporting DELETE operation on workflow event? with deleted reason?
* @mj - can a note be added to a workflow event during creation?
* @mj - is deletedReason still a supported field.
* @mj - is linkText used/needed or valid?
* @bpurdy - notes method does not have tql_filter.
* @mj - TQL keyword deletedReason valid?
* @mj - TQL keyword link required? does not appear to be useful.
* @mj - TQL keyword linkText valid?

## Workflow Template

* @mj - what is targetType field for? is this not the same as assignee type?
* @mj - TQL keyword assignedGroupId valid?
* @mj - TQL keyword assignedUserId valid?
```
        {
            "keyword": "assignedGroupId",
            "name": "Assigned Group ID",
            "type": "Integer",
            "description": "The ID of the Group assigned to this template"
        },
        {
            "keyword": "assignedUserId",
            "name": "Assigned User ID",
            "type": "Integer",
            "description": "The ID of the User assigned to this template"
        },
```
* @mj - TQL keyword configArtifact valid?
* @mj - TQL keyword configPlaybook valid?
* @mj - TQL keyword configTask valid?
* @mj - TQL keyword for organizationId valid?
