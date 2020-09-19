# -*- coding: utf-8 -*-
#
# check_copyright_headers.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.


"""Script to check if all files have a proper copyright header.
This script checks the copyright headers of all C/C++/SLI/Python files
in the source code against the corresponding templates defined in
"doc/copyright_header.*". It uses the variable NEST_SOURCES to
determine the source directory to check.
This script is supposed to be run from static_code_analysis.sh either
during the run of the CI or invocation of check_code_style.sh.
In order to ease error reporting in this context, this script uses two
distinct output channels: messages meant for immediate display are
printed to stderr using the helper function eprint(). Messages meant
for the summary at the end of static_code_analysis.sh are printed to
stdout instead so they can be more easily captured and only printed if
errors occured.
"""

"""
This script was based on/adapted from:

https://github.com/nest/nest-simulator/blob/master/extras/check_copyright_headers.py
"""

import os
import sys
import re


def eprint(*args, **kwargs):
    """Convenience function to print to stderr instead of stdout"""
    print(*args, file=sys.stderr, **kwargs)


EXIT_SUCCESS = 0
EXIT_BAD_HEADER = 1

#source_dir = "/home/travis/build/nest/nestml"
source_dir = "/home/archels/nestml-fork-pycodestyle/nestml"

exclude_dirs = [
    '.git',
    'pynestml/generated',
    'extras',
    'build',
    'doc'
]

# match all file names against these regular expressions. if a match
# is found the file is excluded from the check
exclude_file_patterns = ['\.#.*', '#.*', '.*~', '.*.bak']
exclude_file_regex = [re.compile(pattern) for pattern in exclude_file_patterns]

exclude_files = [
]

templates = {
    ('py', 'pyx', 'pxd'): 'py',
}

template_contents = {}
for extensions, template_ext in templates.items():
    template_name = os.path.join(source_dir, "extras/codeanalysis/copyright_header_template." + template_ext)
    with open(template_name) as template_file:
        template = template_file.readlines()
        for ext in extensions:
            template_contents[ext] = template

total_files = 0
total_errors = 0
for dirpath, _, fnames in os.walk(source_dir):
    if any([exclude_dir in dirpath for exclude_dir in exclude_dirs]):
        continue

    for fname in fnames:
        if any([regex.search(fname) for regex in exclude_file_regex]):
            continue

        extension = os.path.splitext(fname)[1][1:]
        if not (extension and extension in template_contents.keys()):
            continue

        tested_file = os.path.join(dirpath, fname)

        if any([exclude_file in tested_file
                for exclude_file in exclude_files]):
            continue

        with open(tested_file, encoding='utf-8') as source_file:
            total_files += 1
            for template_line in template_contents[extension]:
                try:
                    line_src = source_file.readline()
                except UnicodeDecodeError as err:
                    print("Unable to decode bytes in '{0}': {1}".format(tested_file, err))
                    total_errors += 1
                    break
                if (extension == 'py' and line_src.strip() == '#!/usr/bin/env python3'):
                    line_src = source_file.readline()
                line_exp = template_line.replace('{{file_name}}', fname)
                if line_src != line_exp:
                    fname = os.path.relpath(tested_file)
                    eprint("[COPYRIGHT-HEADER-CHECK] {0}: expected '{1}', found '{2}'.".format(
                        fname, line_exp.rstrip('\n'), line_src.rstrip('\n')))
                    print("... {}\\n".format(fname))
                    total_errors += 1
                    break

print("{0} out of {1} files have an erroneous copyright header.".format(
    total_errors, total_files))

if total_errors > 0:
    sys.exit(EXIT_BAD_HEADER)
else:
    sys.exit(EXIT_SUCCESS)
