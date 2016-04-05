import sys
output = open('pythonVersion.tmp', 'w')
output.write(str(sys.version_info >= (2, 7)))