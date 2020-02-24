# pip install sphinx sphinx_rtd_theme
# pip install CommonMark==0.5.5 recommonmark
# pip install reno

# pip install -r requirements.txt

# used to generate project rst files
# sphinx-apidoc -f -e -o tcex_docs ../../tcex

# temp update bin directory
# touch ../../bin/__init__.py
# ln -fs tcinit ../../bin/tcinit.py
# ln -fs tclib ../../bin/tclib.py
# ln -fs tcpackage ../../bin/tcpackage.py
# ln -fs tcprofile ../../bin/tcprofile.py
# ln -fs tcrun ../../bin/tcrun.py
# ln -fs tctest ../../bin/tctest.py
# ln -fs tcvalidate ../../bin/tcvalidate.py

# get app deployment
wget https://raw.githubusercontent.com/ThreatConnect-Inc/threatconnect-developer-docs/master/docs/deployment_config.rst --output-document=deployment_config.rst

# clean old build
rm -fr _build
rm -fr ../_modules/*
rm -fr ../_sources/*
rm -fr ../*.html
rm -fr ../tcex_docs/*

# generate html
make html

# move the html into place
cp -pr _build/html/* ..

# github pages configuration
touch ../.nojekyll

# remove old files
rm -fr _build

# cleanup bin directory
# rm -f ../../bin/__init__.py
# unlink ../../bin/tcinit.py
# unlink ../../bin/tclib.py
# unlink ../../bin/tcpackage.py
# unlink ../../bin/tcprofile.py
# unlink ../../bin/tcrun.py
# unlink ../../bin/tctest.py
# unlink ../../bin/tcvalidate.py

# cleanup
rm -f deployment_config.rst
rm -fr ../_static/fonts/Lato/

cd ../../
pre-commit run pretty-format-json --all-files
pre-commit run end-of-file-fixer --all-files
