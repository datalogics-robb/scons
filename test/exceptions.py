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

import os
import string
import sys
import TestSCons
import TestCmd

python = TestSCons.python

test = TestSCons.TestSCons(match = TestCmd.match_re_dotall)

test.write('SConstruct', """
def func(source = None, target = None, env = None):
    raise "func exception"
B = Builder(action = func)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')
""")

test.write('foo.in', "foo.in\n")

expected_stderr = """scons: \*\*\* \[foo.out\] Exception
Traceback \((most recent call|innermost) last\):
(  File ".+", line \d+, in \S+
    [^\n]+
)*(  File ".+", line \d+, in \S+
)*(  File ".+", line \d+, in \S+
    [^\n]+
)*  File "SConstruct", line 3, in func
    raise "func exception"
func exception
"""

test.run(arguments = "foo.out", stderr = expected_stderr, status = 2)

test.run(arguments = "-j2 foo.out", stderr = expected_stderr, status = 2)


# Verify that exceptions caused by exit values of builder actions are
# correctly signalled, for both Serial and Parallel jobs.

test.write('myfail.py', r"""\
import sys
sys.exit(1)
""")

test.write('SConstruct', """
Fail = Builder(action = r'%s myfail.py $TARGETS $SOURCE')
env = Environment(BUILDERS = { 'Fail' : Fail })
env.Fail(target = 'f1', source = 'f1.in')
""" % (python))

test.write('f1.in', "f1.in\n")

expected_stderr = "scons: \*\*\* \[f1\] Error 1\n"

test.run(arguments = '.', status = 2, stderr = expected_stderr)
test.run(arguments = '-j2 .', status = 2, stderr = expected_stderr)


# Verify that all exceptions from simultaneous tasks are reported,
# even if the exception is raised during the Task.prepare()
# [Node.prepare()]

test.write('SConstruct', """
Fail = Builder(action = r'%s myfail.py $TARGETS $SOURCE')
env = Environment(BUILDERS = { 'Fail' : Fail })
env.Fail(target = 'f1', source = 'f1.in')
env.Fail(target = 'f2', source = 'f2.in')
env.Fail(target = 'f3', source = 'f3.in')
""" % (python))

# f2.in is not created to cause a Task.prepare exception
test.write('f3.in', 'f3.in\n')

# In Serial task mode, get the first exception and stop
test.run(arguments = '.', status = 2, stderr = expected_stderr)

# In Parallel task mode, we will get all three exceptions.

expected_stderr_list = [
    "scons: *** [f1] Error 1\n",
    "scons: *** Source `f2.in' not found, needed by target `f2'.  Stop.\n",
    "scons: *** [f3] Error 1\n",
]

# To get all three exceptions simultaneously, we must execute -j7 to
# create one thread each for the SConstruct file and f[123] and f[123].in.

test.run(arguments = '-j7 .', status = 2, stderr = None)

missing = []
for es in expected_stderr_list:
    if string.find(test.stderr(), es) == -1:
        missing.append(es)

if missing:
    sys.stderr.write("Missing the following lines from stderr:\n")
    for m in missing:
        sys.stderr.write(m)
    sys.stderr.write('STDERR ===============================================\n')
    sys.stderr.write(test.stderr())
    test.fail_test(1)


test.pass_test()
