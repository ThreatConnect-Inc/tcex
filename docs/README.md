# Requirements
pip install sphinx sphinx_rtd_theme
pip install CommonMark==0.5.5 recommonmark
pip install reno

# Build Docs
sphinx-apidoc -f -o tcex ../tcex/
make html
