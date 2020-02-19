Installing NESTML
=================

Please note that only Python 3 is supported. The instructions below assume that `python` is aliased to or refers to `python3`, and `pip` to `pip3`.

Installing the latest release from PyPI
---------------------------------------

The easiest way to install NESTML is to use the [Python Package Index (PyPI)](https://pypi.org). This requires the Python package management system `pip` to be installed. In Ubuntu, Mint and Debian Linux you can install `pip` as follows:

```
sudo apt install python3-pip
```

NESTML can then be installed into your local user directory via:

```
pip install nestml --user
```

Installing the latest development version from GitHub
-----------------------------------------------------

To obtain the latest development version, clone directly from the master branch of the GitHub repository:

```
git clone https://github.com/nest/nestml
```

Install into your local user directory using:

```
cd nestml
python setup.py install --user
```

Testing
-------

After installation, correct operation can be tested by:

```
python setup.py test
```
