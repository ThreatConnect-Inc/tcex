# pip install sphinx sphinx_rtd_theme
# pip install CommonMark==0.5.5 recommonmark
# pip install reno

# used to generate project rst files
# sphinx-apidoc -f -e -o tcex_docs ../../tcex

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
