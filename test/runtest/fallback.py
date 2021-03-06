#!/usr/bin/env python
#
# __COPYRIGHT__
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

"""
Test that runtest.py falls back (with a warning) using --noqmtest
if it can't find qmtest.py on the $PATH.
"""

import os
import os.path
import re
import string

import TestRuntest

python = TestRuntest.python
_python_ = TestRuntest._python_

test = TestRuntest.TestRuntest(noqmtest=1)

qmtest_py = test.where_is('qmtest.py')

if qmtest_py:
    dir = os.path.split(qmtest_py)[0]
    path = string.split(os.environ['PATH'], os.pathsep)
    path.remove(dir)
    os.environ['PATH'] = string.join(path, os.pathsep)

test.subdir('test')

test_pass_py = os.path.join('test', 'pass.py')
test_fail_py = os.path.join('test', 'fail.py')
test_no_result_py = os.path.join('test', 'no_result.py')

workpath_pass_py = test.workpath(test_pass_py)
workpath_fail_py = test.workpath(test_fail_py)
workpath_no_result_py = test.workpath(test_no_result_py)

test.write_failing_test(test_fail_py)
test.write_no_result_test(test_no_result_py)
test.write_passing_test(test_pass_py)

if re.search('\s', python):
    expect_python = _python_
else:
    expect_python = python

expect_stdout = """\
%(expect_python)s -tt %(workpath_fail_py)s
FAILING TEST STDOUT
%(expect_python)s -tt %(workpath_no_result_py)s
NO RESULT TEST STDOUT
%(expect_python)s -tt %(workpath_pass_py)s
PASSING TEST STDOUT

Failed the following test:
\t%(test_fail_py)s

NO RESULT from the following test:
\t%(test_no_result_py)s
""" % locals()

expect_stderr = """\
Warning:  qmtest.py not found on $PATH, assuming --noqmtest option.
FAILING TEST STDERR
NO RESULT TEST STDERR
PASSING TEST STDERR
"""

testlist = [
    test_fail_py,
    test_no_result_py,
    test_pass_py,
]

test.run(arguments = string.join(testlist),
         status = 1,
         stdout = expect_stdout,
         stderr = expect_stderr)

test.pass_test()
