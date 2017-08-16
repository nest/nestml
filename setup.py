from distutils.core import setup

setup(
    name='PyNESTML',
    packages=['src.main.python.org.frontend',
              'src.main.python.org.nestml.ast',
              'src.main.python.org.nestml.parser',
              'src.main.python.org.nestml.visitor',
              'target.src.main.grammars.org'],

)
