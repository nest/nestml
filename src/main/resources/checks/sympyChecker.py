import sympy
from distutils.version import LooseVersion, StrictVersion

output = open('sympyVersion.tmp', 'w')
output.write(str(LooseVersion(sympy.__version__) >= LooseVersion("1.0")))
