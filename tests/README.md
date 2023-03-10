# Prerequisites

-   A Group must be create in the TC instance (Org Settings -> Groups)
-   The Description Attribute must include Case and URL (System Settings -> Attribute Types)
-   A Service App needs to be created "DO NOT DELETE - TcEx Test Service App"
-   The v3ApiIntelLinkLimit system property needs to be set to 2.

## Code Stats

```bash
> cloc bin tcex tests
     567 text files.
     497 unique files.
     674 files ignored.

github.com/AlDanial/cloc v 1.94  T=0.82 s (606.1 files/s, 110333.3 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Python                         463          12769          19781          48249
JSON                            28              0              0           8705
YAML                             1              1              9            394
Markdown                         4            172              0            391
Text                             1              0              0              1
-------------------------------------------------------------------------------
SUM:                           497          12942          19790          57740
-------------------------------------------------------------------------------
```

## General Test Command

2022-08-26 - 1,721 Test Cases

## Test a specific module

pytest tests/api/tc/v2/batch/

## Test a specific file

pytest tests/case_management/test_artifact_interface.py

## Test a specific test case in a file

pytest tests/case_management/test_artifact_interface.py::test_artifact_type_api_options

## Basic Full Run

```bash
pytest -n auto --dist loadgroup tests
```

## Coverage Testing w/ Coverage and HTML Report

```bash
pytest \
  -n auto --dist loadgroup \
  --cov=. --cov-report=term-missing --cov-report=html:tests/reports/cov-report \
  --durations=25 \
  --html=tests/reports/tcex-report.html --self-contained-html \
  --log-file=pytest.log \
  tests || pytest tests --last-failed --last-failed-no-failures none
```

### Results

1,788 Test Cases

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                   16855   4367    74%
```

# Module Testing

## api/tc

### v2

616 Test Cases

```bash
pytest -n auto --dist loadgroup --cov=tcex/api/tc/v2/ --cov-report=term-missing tests/api/tc/v2/
```

#### Results

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                    4316   1402    68%
```

#### batch

203 Test Cases

```bash
pytest -n auto --cov=tcex/api/tc/v2/batch --cov-report=term-missing tests/api/tc/v2/batch
```

#### Results

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                    1627    560    66%
```

#### datastore

20 Test Cases

```bash
pytest -n auto --cov=tcex/api/tc/v2/datastore --cov-report=term-missing tests/api/tc/v2/datastore
```

#### Results

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                     151      3    98%
```

#### metrics

4 Test Cases

```bash
pytest -n 4 --cov=tcex/api/tc/v2/metric --cov-report=term-missing tests/api/tc/v2/metric
```

#### Results

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                      64      1    98%
```

#### notifications

3 Test Cases

```bash
pytest -n 3 --cov=tcex/api/tc/v2/notification --cov-report=term-missing tests/api/tc/v2/notification
```

#### Results

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                      35      1    97%
```

#### threat_intelligence

387 Test Cases

```bash
pytest -n auto --cov=tcex/api/tc/v2/threat_intelligence --cov-report=term-missing tests/api/tc/v2/threat_intelligence
```

#### Results

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                    2396    836    65%
```

### v3

169 Test Cases

```bash
pytest -n auto --cov=tcex/api/tc/v3/ --cov-report=term-missing tests/api/tc/v3/
```

#### Results

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                    4426    718    84%
```

#### artifact_types

```bash
pytest --cov=tcex/api/tc/v3/artifact_types --cov-report=term-missing tests/api/tc/v3/artifact_types
```

#### artifacts

```bash
pytest --cov=tcex/api/tc/v3/artifacts --cov-report=term-missing tests/api/tc/v3/artifacts
```

#### attribute_types

```bash
pytest --cov=tcex/api/tc/v3/attribute_types --cov-report=term-missing tests/api/tc/v3/attribute_types
```

#### case_attributes

```bash
pytest --cov=tcex/api/tc/v3/case_attributes --cov-report=term-missing tests/api/tc/v3/case_attributes/
```

#### cases

```bash
pytest --cov=tcex/api/tc/v3/cases --cov-report=term-missing tests/api/tc/v3/cases/
```

#### group_attributes

```bash
pytest --cov=tcex/api/tc/v3/group_attributes --cov-report=term-missing tests/api/tc/v3/group_attributes/
```

#### groups

```bash
pytest --cov=tcex/api/tc/v3/groups --cov-report=term-missing tests/api/tc/v3/groups/
```

#### indicator_attributes

```bash
pytest --cov=tcex/api/tc/v3/indicator_attributes --cov-report=term-missing tests/api/tc/v3/indicator_attributes/
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

#### security_labels

```bash
pytest --cov=tcex/api/tc/v3/security_labels --cov-report=term-missing tests/api/tc/v3/security_labels
```

#### tag

```bash
pytest --cov=tcex/api/tc/v3/tag --cov-report=term-missing tests/api/tc/v3/tag
```

#### tasks

```bash
pytest --cov=tcex/api/tc/v3/tasks --cov-report=term-missing tests/api/tc/v3/tasks
```

#### victim_assets

```bash
pytest --cov=tcex/api/tc/v3/victim_assets --cov-report=term-missing tests/api/tc/v3/victim_assets
```

#### victim_attributes

```bash
pytest --cov=tcex/api/tc/v3/victim_attributes --cov-report=term-missing tests/api/tc/v3/victim_attributes
```

#### victims

```bash
pytest --cov=tcex/api/tc/v3/tasks --cov-report=term-missing tests/api/tc/v3/tasks
```

#### workflow_events

```bash
pytest --cov=tcex/api/tc/v3/workflow_events --cov-report=term-missing tests/api/tc/v3/workflow_events
```

#### workflow_templates

```bash
pytest --cov=tcex/api/tc/v3/workflow_templates --cov-report=term-missing tests/api/tc/v3/workflow_templates
```

## app/config


```bash
pytest -n auto --cov=tcex/app/config/ --cov-report=term-missing tests/app/config/
```

### Results

48 Test Cases

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                    1411    357    75%
```
## app/decorator

```bash
pytest -n auto --cov=tcex/app/decorator/ --cov-report=term-missing tests/app/decorator/
```

### Results

42 Test Cases

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                     163      0   100%
```

## app/playbook


```bash
pytest -n auto --cov=tcex/app/playbook/ --cov-report=term-missing tests/app/playbook/
```

### Results

318 Test Cases

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                     647     50    92%
```

## app/token


```bash
pytest -n 8 --cov=tcex/app/token/ --cov-report=term-missing tests/app/token_/
```

### Results

9 Test Cases

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                     139      5    96%
```

## bin

11 Test Cases

```bash
pytest -n 8 --cov=tcex/bin/ --cov-report=term-missing tests/bin/
```

## exit

```bash
pytest -n 6 --cov=tcex/exit/ --cov-report=term-missing tests/exit/
```

### Results

4 Test Cases

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                     110     55    50%
```

## input

```bash
pytest -n auto --cov=tcex/input/ --cov-report=term-missing tests/input/
```

### Results

397 Test Cases

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                    965    122    87%
```

## logger

```bash
pytest -n 5 --cov=tcex/logger/ --cov-report=term-missing tests/logger/
```

### Results

9 Test Cases

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                     324     56    83%
```

## requests_session

```bash
pytest -n auto --cov=tcex/requests_session/ --cov-report=term-missing tests/requests_session/
```
### Results

20 Cases

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                     351     29    92%
```

## util

```bash
pytest -n auto --cov=tcex/util/ --cov-report=term-missing tests/util/
```

### Results

187 Test Cases

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                     473      0   100%
```
