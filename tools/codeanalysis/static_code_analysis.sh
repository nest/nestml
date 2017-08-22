#!/bin/bash

# static_code_analysis.sh
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


# This shell script is part of the NEST Travis CI build and test environment.
# It performs the static code analysis and is invoked by 'build.sh'.
# The script is also executed when running 'check_code_style.sh' for
# a local static code analysis.
#
# NOTE: This shell script is tightly coupled to Python script
#       'extras/parse_travis_log.py'. 
#       Any changes to message numbers (MSGBLDnnnn) have effects on 
#       the build/test-log parsing process.
#

# Command line parameters.
INCREMENTAL=${1}              # true or false, user needs to confirm befor checking a source file.
FILE_NAMES=${2}               # The list of files or a single file to be checked.
VERA=${3}                     # Name of the VERA++ executable.
CPPCHECK=${4}                 # Name of the CPPCHECK executable.
CLANG_FORMAT=${5}             # Name of the CLANG-FORMAT executable.
PEP8=${6}                     # Name of the PEP8 executable.
PERFORM_VERA=${7}             # true or false, indicating whether VERA++ analysis is performed or not.
PERFORM_CPPCHECK=${8}         # true or false, indicating whether CPPCHECK analysis is performed or not.
PERFORM_CLANG_FORMAT=${9}     # true or false, indicating whether CLANG-FORMAT analysis is performed or not.
PERFORM_PEP8=${10}            # true or false, indicating whether PEP8 analysis is performed or not.
IGNORE_MSG_VERA=${11}         # true or false, indicating whether VERA++ messages should accout for the build result.
IGNORE_MSG_CPPCHECK=${12}     # true or false, indicating whether CPPCHECK messages should accout for the build result.
IGNORE_MSG_CLANG_FORMAT=${13} # true or false, indicating whether CLANG-FORMAT messages should accout for the build result.
IGNORE_MSG_PEP8=${14}         # true or false, indicating whether PEP8 messages should accout for the build result.

# PEP8 rules to ignore.
PEP8_IGNORES="E121,E123,E126,E226,E24,E704,E501"

# Drop files that should not be checked (space-separated list).
FILES_TO_IGNORE=""

# Print version information.
echo "Following tools are in use:"
echo "---------------------------"
if $PERFORM_VERA; then
  VERA_VERS=`$VERA --version`
  echo "VERA++       : $VERA_VERS"
fi
if $PERFORM_CPPCHECK; then
  CPPCHECK_VERS=`$CPPCHECK --version | sed 's/^Cppcheck //'`
  echo "CPPCHECK     : $CPPCHECK_VERS"
fi
if $PERFORM_CLANG_FORMAT; then
  CLANG_FORMAT_VERS=`$CLANG_FORMAT --version`
  echo "CLANG-FORMAT : $CLANG_FORMAT_VERS"
fi
if $PERFORM_PEP8; then
  PEP8_VERS=`$PEP8 --version`
  echo "PEP8         : $PEP8_VERS"
fi
echo ""

# Perfom static code analysis.
c_files_with_errors=""
python_files_with_errors=""
for f in $FILE_NAMES; do

  if [[ $FILES_TO_IGNORE =~ .*$f.* ]]; then
    echo "$f is explicitly ignored."
    continue
  fi   
  if [ ! -f "$f" ]; then
    echo "$f is not a file or does not exist anymore."
    continue
  fi
  if $INCREMENTAL; then
    echo ""
    echo "Press [Enter] to continue.  (Static code analysis for file $f.)"
    read continue
  fi

  case $f in
    *.h | *.c | *.cc | *.hpp | *.cpp )
      vera_failed=false
      cppcheck_failed=false
      clang_format_failed=false

      f_base=`basename $f`

      # VERA++
      if $PERFORM_VERA; then
        echo "Running VERA++ .....: $f"
        $VERA --profile nest $f > ${f_base}_vera.txt 2>&1
        if [ -s "${f_base}_vera.txt" ]; then
          vera_failed=true
          cat ${f_base}_vera.txt | while read line
          do
            echo "[VERA] $line"
          done
        fi
        rm ${f_base}_vera.txt
      fi

      # CPPCHECK
      if $PERFORM_CPPCHECK; then
        echo "Running CPPCHECK ...: $f"
        $CPPCHECK --enable=all --inconclusive --std=c++03 --suppress=missingIncludeSystem $f > ${f_base}_cppcheck.txt 2>&1
        # Remove the header, the first line.
        tail -n +2 "${f_base}_cppcheck.txt" > "${f_base}_cppcheck.tmp" && mv "${f_base}_cppcheck.tmp" "${f_base}_cppcheck.txt"
        if [ -s "${f_base}_cppcheck.txt" ]; then
          cppcheck_failed=true
          typeset -i msg_count=0
          cat ${f_base}_cppcheck.txt | while read line
          do
            echo "[CPPC] $line"
          done
        fi
        rm ${f_base}_cppcheck.txt
      fi

      # CLANG-FORMAT
      if $PERFORM_CLANG_FORMAT; then
        echo "Running CLANG-FORMAT: $f"
        # Create a clang-format formatted temporary file and perform a diff with its origin.
        file_formatted="${f_base}_formatted.txt"
        file_diff="${f_base}_diff.txt"
        $CLANG_FORMAT $f > $file_formatted
        diff $f $file_formatted > $file_diff 2>&1
        if [ -s "$file_diff" ]; then
          clang_format_failed=true
          cat $file_diff | while read line
          do
            echo "[DIFF] $line"
          done
        fi
        rm $file_formatted
        rm $file_diff
      fi

      # Add the file to the list of files with format errors.
      if $vera_failed || $cppcheck_failed || $clang_format_failed; then
        c_files_with_errors="$c_files_with_errors $f"
      fi
      ;;

    *.py )
      # PEP8
      if $PERFORM_PEP8; then
        echo "Running PEP8 .......: $f"
        if ! pep8_result=`$PEP8 --ignore=$PEP8_IGNORES $f` ; then
          printf '%s\n' "$pep8_result" | while IFS= read -r line
          do
            echo "[PEP8] $line"
          done
          # Add the file to the list of files with format errors.
          python_files_with_errors="$python_files_with_errors $f"
        fi
      fi
      ;;

    *)
      echo "Skipping ...........: $f  (not a C/C++/Python file)"
      continue
  esac
done

if [ "x$c_files_with_errors" != "x" ] || [ "x$python_files_with_errors" != "x" ]; then
  echo ""
  echo "+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +"
  echo "+                 STATIC CODE ANALYSIS DETECTED PROBLEMS !                    +"
  echo "+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +"
  echo ""
  if [ "x$c_files_with_errors" != "x" ]; then
    echo "C/C++ files with formatting errors:"
    for f in $c_files_with_errors; do
      echo "... $f"
    done
    echo "Run $CLANG_FORMAT -i <filename> for autocorrection."
    echo ""
  fi

  if [ "x$python_files_with_errors" != "x" ]; then
    echo "Python files with formatting errors:"
    for f in $python_files_with_errors; do
      echo "... $f"
    done
    echo "Run pep8ify -w <filename> for autocorrection."
    echo ""
  fi
  
  echo "For other problems, please correct your code according to the [VERA], [CPPC], [DIFF], and [PEP8] messages above."
else
  echo ""
  echo "+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +"
  echo "+               STATIC CODE ANALYSIS TERMINATED SUCCESSFULLY !                +"
  echo "+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +"
  echo ""  
fi
