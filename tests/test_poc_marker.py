# -*- coding: utf-8 -*-
"""
PoC test - security research. Proves untrusted PR code executes in CI.
"""
import sys


def test_poc_marker():
    marker = "NESTML_POC_1772094808_jlxhbboy"
    print(marker, flush=True)
    sys.stdout.flush()
    assert True
