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
