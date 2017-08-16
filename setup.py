from distutils.core import setup

setup(
    name='PyNESTML',
    packages=['pynestml.src.main.python.org.frontend',
              'pynestml.src.main.python.org.nestml.ast',
              'pynestml.src.main.python.org.nestml.parser',
              'pynestml.src.main.python.org.nestml.visitor',
              'pynestml.src.main.grammars.org'],

)
