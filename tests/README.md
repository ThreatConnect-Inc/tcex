# Prerequisites

-   A Group must be create in the TC instance (Org Settings -> Groups)
-   The Description Attribute must include Case and URL (System Settings -> Attribute Types)
-   A Service App needs to be created "DO NOT DELETE - TcEx Test Service App"

## Code Stats

```bash
> cloc bin tcex tests
     539 text files.
     468 unique files.
    1478 files ignored.

github.com/AlDanial/cloc v 1.94  T=0.75 s (626.8 files/s, 112645.6 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Python                         430          12024          19155          44170
JSON                            32              0              0           7800
YAML                             1              1              9            394
Markdown                         4            173              0            377
Text                             1              0              0              1
-------------------------------------------------------------------------------
SUM:                           468          12198          19164          52742
-------------------------------------------------------------------------------
```

## General Test Command

2022-08-26 - 1,721 Test Cases

## Test a specific module

pytest tests/batch

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

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                   13959   3314    76%
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
pytest -n 4 --cov=tcex/api/tc/v2/metrics --cov-report=term-missing tests/api/tc/v2/metrics
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
pytest -n 3 --cov=tcex/api/tc/v2/notifications --cov-report=term-missing tests/api/tc/v2/notifications
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

## app_config

44 Test Cases

```bash
pytest -n auto --cov=tcex/app_config/ --cov-report=term-missing tests/app_config/
```

### Results

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                     850      8    99%
```

## app_feature

6 Test Cases

```bash
pytest -n 6 --cov=tcex/app_feature/ --cov-report=term-missing tests/app_feature/
```

### Results

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                      67      2    97%
```

## bin

8 Test Cases

```bash
pytest -n 8 --cov=tcex/bin/ --cov-report=term-missing tests/bin/
```

## decorators

36 Test Cases

```bash
pytest -n auto --cov=tcex/decorators/ --cov-report=term-missing tests/decorators/
```

### Results

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                     131      0   100%
```

## input

356 Test Cases

```bash
pytest -n auto --cov=tcex/input/ --cov-report=term-missing tests/input/
```

### Results

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                    898     90    90%
```

## logger

5 Test Cases

```bash
pytest -n 5 --cov=tcex/logger/ --cov-report=term-missing tests/logger/
```

### Results

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                     293     68    77%
```

## playbooks

289 Test Cases

```bash
pytest -n auto --cov=tcex/playbook/ --cov-report=term-missing tests/playbook/
```

### Results

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                     513     20    96%
```

## sessions

17 Cases

```bash
pytest -n auto --cov=tcex/sessions/ --cov-report=term-missing tests/sessions/
```

### Results

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                     293     40    86%
```

## tcex methods

3 Test Cases

```bash
pytest tests/tcex_methods/
```

### Results

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
```

## tokens

8 Test Cases

```bash
pytest -n 8 --cov=tcex/tokens/ --cov-report=term-missing tests/tokens/
```

### Results

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                     132      5    96%
```

## utils

116 Test Cases

```bash
pytest -n auto --cov=tcex/utils/ --cov-report=term-missing tests/utils/
```

### Results

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
TOTAL                                     411    122    70%
```
