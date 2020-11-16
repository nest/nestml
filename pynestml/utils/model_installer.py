# -*- coding: utf-8 -*-
#
# model_installer.py
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
import os
import subprocess
import sys


def install_nest(models_path, nest_path):
    """
    This method can be used to install all models located in the ${models} dir into NEST. For the simulator,
    the path to the installation has to be provided (a.k.a. the -Dwith-nest argument of the make command).
    Caution: The nest_path should only point to the install dir, the suffix  /bin/nest-config is automatically attached.
    """
    if not os.path.isdir(models_path):
        print('PyNestML: Models path not a directory (%s)! abort installation...' % models_path)
        return
    if not os.path.isdir(nest_path):
        print('PyNestML: NEST path not a directory (%s)! abort installation...' % nest_path)
        return

    cmake_cmd = ['cmake', '-Dwith-nest=' + str(nest_path) + '/bin/nest-config', '.']
    make_all_cmd = ['make', 'all']
    make_install_cmd = ['make', 'install']
    # check if we run on win
    if sys.platform.startswith('win'):
        shell = True
    else:
        shell = False

    # first call cmake with all the arguments
    try:
        result = subprocess.check_call(cmake_cmd, stderr=subprocess.STDOUT, shell=shell,
                                       cwd=str(os.path.join(models_path)))
    except subprocess.CalledProcessError as e:
        print('PyNestML: Something went wrong in \'cmake\', see error above!')
        print('abort installation...')
        return

    # now execute make all
    try:
        subprocess.check_call(make_all_cmd, stderr=subprocess.STDOUT, shell=shell,
                              cwd=str(os.path.join(models_path)))
    except subprocess.CalledProcessError as e:
        print('PyNestML: Something went wrong in \'make all\', see error above!')
        print('abort installation...')
        return

    # finally execute make install
    try:
        subprocess.check_call(make_install_cmd, stderr=subprocess.STDOUT, shell=shell,
                              cwd=str(os.path.join(models_path)))
    except subprocess.CalledProcessError as e:
        print('PyNestML: Something went wrong in \'make install\', see error above!')
        print('abort installation...')
        return
