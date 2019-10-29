# Module Testing
pytest tests/batch

# Coverage Testing
pytest --cov=. --cov-report term-missing tests/

# Release Testing Run
pytest --cov=. --cov-report html:tests/reports/cov-report --html=tests/reports/tcex-report.html --self-contained-html tests/
