from os.path import dirname, join
import subprocess
import sys


MY_DIR = dirname(__file__)


def test_jigna_web_does_not_import_qt():
    args = [sys.executable, '-v', join(MY_DIR, 'simple_view_web.py')]
    output = subprocess.check_output(args, stderr=subprocess.STDOUT)
    print output
    assert 'QtCore' not in output, output


if __name__ == '__main__':
    from nose.core import runmodule
    runmodule()
