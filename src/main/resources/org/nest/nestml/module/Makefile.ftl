<#assign lowerModuleName = moduleName?lower_case>
# Automake file for external dynamic modules for NEST
#
# Hans Ekkehard Plesser, April 2008
# Automake file for the Developer Module
#
# lib${lowerModuleName} is built as a normal, installable library.
# It will be installed to $prefix/lib by make install.
#
# Headers from this directory are not to be installed upon
# make install. They are therefore included in _SOURCES.


# 1. Exchange "my" in "mymodule" with the name of your model below
#    (ten locations).
# 2. Add all .cpp and .h files from your code as *_SOURCES. Header files
#    are given only so that they will be included in the tarball if you
#    run "make dist" on your module.
# 3. The mymodule* stuff creates a module that can be loaded at runtime.
#    It is called mymodule.so.
# 4. The libmymodule* stuff creates a library against which NEST can be
#    linked.

libdir= @libdir@/nest

lib_LTLIBRARIES=      ${lowerModuleName}.la lib${lowerModuleName}.la

${lowerModuleName}_la_CXXFLAGS= @AM_CXXFLAGS@
${lowerModuleName}_la_SOURCES=  ${lowerModuleName}Config.cpp      ${lowerModuleName}Config.h      \
<#list neuronModelNames as name>
    ${name}.cpp ${name}.h \
</#list>
    # last line cannot be empty, since the last \ of the sources

${lowerModuleName}_la_LDFLAGS=  -module

lib${lowerModuleName}_la_CXXFLAGS= $(${lowerModuleName}_la_CXXFLAGS) -DLINKED_MODULE
lib${lowerModuleName}_la_SOURCES=  $(${lowerModuleName}_la_SOURCES)

MAKEFLAGS= @MAKE_FLAGS@

AM_CPPFLAGS= @NEST_CPPFLAGS@ \
             @INCLTDL@

.PHONY: install-slidoc

#nobase_pkgdata_DATA=\
#    sli/${lowerModuleName}-init.sli

install-slidoc:
    NESTRCFILENAME=/dev/null $(DESTDIR)$(NEST_PREFIX)/bin/sli --userargs="@HELPDIRS@" $(NEST_PREFIX)/share/nest/sli/install-help.sli

install-data-hook: install-exec install-slidoc

EXTRA_DIST= sli

AUTOMAKE_OPTIONS = subdir-objects
