"""
@author kperun
TODO header
"""


class InvalidPathException(Exception):
    """
    This exception is thrown whenever neither a file nor a dir has been handed over. This should not happen.
    """
    pass


class InvalidTargetException(Exception):
    """
    This exception is thrown whenever a not correct target path has been handed over, e.g. a path to a file.
    """
    pass
