# install black
pip install black

# add python configuration file with settings for black
if [ ! -f pyproject.toml ]; then
echo """[tool.black]
line-length = 100
skip-string-normalization = true
""" >> pyproject.toml
fi

# install black pre-commit
pip install pre-commit

# add pre-commit config
if [ ! -f .pre-commit-config.yaml ]; then
echo """repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v1.2.3
    hooks:
    -   id: check-added-large-files
    -   id: check-ast
    -   id: check-json
    -   id: double-quote-string-fixer
    -   id: end-of-file-fixer
    -   id: fix-encoding-pragma
    -   id: flake8
    -   id: pretty-format-json
        args:
        -   --autofix
    -   id: trailing-whitespace
-   repo: https://github.com/ambv/black
    rev: stable
    hooks:
    -   id: black
        language_version: python3.6
-   repo: https://github.com/pre-commit/mirrors-pylint
    rev: 'master'
    hooks:
    -   id: pylint
        args:
        -    --disable=C0103,C0302,E0401,R0205,R0801,R0902,R0903,R0904,R0912,R0913,R0914,R0915,R1702,W0212,W0511,W0703,W1202

""" >> .pre-commit-config.yaml
fi

# install pre-commit
pre-commit install

# run checks/updates
pre-commit run check-added-large-files --all-files
pre-commit run check-ast --all-files
pre-commit run double-quote-string-fixer --all-files
pre-commit run end-of-file-fixer --all-files
pre-commit run fix-encoding-pragma --all-files
pre-commit run flake8 --all-files
pre-commit run pretty-format-json --all-files
pre-commit run trailing-whitespace --all-files
pre-commit run black --all-files
