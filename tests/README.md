# Module Testing
pytest tests/batch

# Coverage Testing
pytest --cov=. --cov-report term-missing tests/

# Coverage on Single Module
pytest --cov=tcex/case_management/ --cov-report term-missing tests/case_management/
pytest --cov=tcex/utils/ --cov-report term-missing tests/utils/

# Release Testing Run
pytest --cov=. --cov-report html:tests/reports/cov-report --html=tests/reports/tcex-report.html --self-contained-html tests/
