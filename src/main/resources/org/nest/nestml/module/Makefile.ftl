# Automake file for external dynamic modules for NEST
#
# Hans Ekkehard Plesser, April 2008
# Automake file for the Developer Module
#
# lib${moduleName} is built as a normal, installable library.
# It will be installed to $prefix/lib by make install.
#
# Headers from this directory are not to be installed upon
# make install. They are therefore included in _SOURCES.

libdir= @libdir@/nest

# We need to install the module header for static linking on BlueGene
include_HEADERS = ${moduleName}Config.h

# All other source files
source_files=  ${moduleName}Config.cpp \
<#list neurons as neuron>
    ${neuron.getName()}.cpp ${neuron.getName()}.h
</#list>

if BUILD_DYNAMIC_USER_MODULES
  lib_LTLIBRARIES= lib${moduleName}.la ${moduleName}.la
  ${moduleName}_la_CXXFLAGS= @AM_CXXFLAGS@
  ${moduleName}_la_SOURCES=  $(source_files)
  ${moduleName}_la_LDFLAGS=  -module
else
  lib_LTLIBRARIES= lib${moduleName}.la
endif

lib${moduleName}_la_CXXFLAGS= @AM_CXXFLAGS@ -DLINKED_MODULE
lib${moduleName}_la_SOURCES=  $(source_files)

MAKEFLAGS= @MAKE_FLAGS@

AM_CPPFLAGS= @NEST_CPPFLAGS@ \
@INCLTDL@

.PHONY: install-slidoc

pkgdatadir=@datadir@/nest

# TODO: FixMe
#nobase_pkgdata_DATA=sli/${moduleName}-init.sli

install-slidoc:NESTRCFILENAME=/dev/null $(DESTDIR)$(NEST_PREFIX)/bin/sli --userargs="@HELPDIRS@" $(NEST_PREFIX)/share/nest/sli/install-help.sli

install-data-hook: install-exec install-slidoc

EXTRA_DIST= sli