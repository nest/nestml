#!/usr/bin/tclsh

# vera++.profile
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

# This file needs to be added to to the VERA++ profiles.
# sudo cp ./tools/codeanalysis/vera++.profile /usr/lib/vera++/profiles/nestml
#
# This profile includes all the rules for checking PyNestML
#
# Do not apply T011 (curly braces), since that can get confused
# by conditional code inclusion.
#
# Do not apply F002 (file name length limits), since some benign model file
# names then become illegal; Vera++ 1.2.1 does not support parameters in
# profile files, so we cannot extend file name length limits here. 
#
# Do not apply L006 (limit on file length), since some legacy sli code 
# is too long; see also F002.

set rules {
  F001
  L001
  L002
  L003
  L005
  T001
  T004
  T005
  T006
  T007
  T010
  T012
  T013
  T017
  T018
  T019
}
