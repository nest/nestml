# -*- coding: utf-8 -*-
#
# nest_tools.py
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

import subprocess
import sys
import tempfile

from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel


class NESTTools:
    r"""Helper functions for NEST Simulator"""

    @classmethod
    def detect_nest_version(cls) -> str:
        r"""Auto-detect NEST Simulator installed version. The returned string corresponds to a git tag or git branch name.

        Do this in a separate process to avoid potential side-effects of import the ``nest`` Python module.

        .. admonition::

           NEST version detection needs improvement. See https://github.com/nest/nest-simulator/issues/2116
        """

        script = """\"\"\"Auto-detect NEST Simulator installed version and print the version string to stderr.\"\"\"

import sys

try:
    import nest

    try:
        if "DataConnect" in dir(nest):
            nest_version = "v2.20.2"
        else:
            nest_version = "v" + nest.ll_api.sli_func("statusdict/version ::")
            if "post0.dev0" in nest_version:
                nest_version = "master"
    except:
        pass

except ModuleNotFoundError:
    nest_version = ""

print(nest_version, file=sys.stderr)
"""

        with tempfile.NamedTemporaryFile() as f:
            f.write(bytes(script, encoding="UTF-8"))
            f.seek(0)
            cmd = [sys.executable, f.name]

            process = subprocess.Popen(cmd, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            nest_version = stderr.decode("UTF-8").strip()

        if nest_version == "":
            Logger.log_message(None, -1, "An error occurred while importing the `nest` module in Python. Please check your NEST installation-related environment variables and paths, or specify ``nest_version`` manually in the code generator options.", None, LoggingLevel.ERROR)
            sys.exit(1)

        Logger.log_message(None, -1, "The NEST Simulator version was automatically detected as: " + nest_version, None, LoggingLevel.INFO)

        return nest_version
