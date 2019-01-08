# pip install sphinx sphinx_rtd_theme
# pip install CommonMark==0.5.5 recommonmark
# pip install reno

# pip install -r requirements.txt

# used to generate project rst files
# sphinx-apidoc -f -e -o tcex_docs ../../tcex

# temp update bin directory
touch ../../bin/__init__.py
ln -fs tcinit ../../bin/tcinit.py
ln -fs tclib ../../bin/tclib.py
ln -fs tcpackage ../../bin/tcpackage.py
ln -fs tcprofile ../../bin/tcprofile.py
ln -fs tcrun ../../bin/tcrun.py

# clean old build
rm -fr _build

# generate html
make html

# move the html into place
cp -pr _build/html/* ..

# github pages configuration
touch ../.nojekyll

# remove old files
rm -fr _build

# cleanup bin directory
rm -f ../../bin/__init__.py
unlink ../../bin/tcinit.py
unlink ../../bin/tclib.py
unlink ../../bin/tcpackage.py
unlink ../../bin/tcprofile.py
unlink ../../bin/tcrun.py
