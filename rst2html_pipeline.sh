#!/bin/bash

cp pynestml/codegeneration/resources_autodoc/autodoc.css /tmp/_autodoc.css
pygmentize -S default -f html -a .code >> /tmp/_autodoc.css

cd pynestml/codegeneration/resources_autodoc
rst2html --stylesheet=/tmp/_autodoc.css /tmp/nestml-autodoc/izhikevich.rst > /tmp/nestml-autodoc/izhikevich.html
cd ../..
