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

import string
import StringIO
import sys

import TestSCons

test = TestSCons.TestSCons()

try:
    import pstats
except ImportError:
    test.skip_test('No pstats module, skipping test.\n')

test.write('SConstruct', """\
Command('file.out', 'file.in', Copy("$TARGET", "$SOURCE"))
""")

test.write('file.in', "file.in\n")

scons_prof = test.workpath('scons.prof')

test.run(arguments = "--profile=%s -h" % scons_prof)
test.fail_test(string.find(test.stdout(), 'usage: scons [OPTION]') == -1)
test.fail_test(string.find(test.stdout(), 'usage: scons [OPTION]') == -1)

stats = pstats.Stats(scons_prof)
stats.sort_stats('time')

try:
    save_stdout = sys.stdout
    sys.stdout = StringIO.StringIO()

    stats.strip_dirs().print_stats()

    s = sys.stdout.getvalue()
finally:
    sys.stdout = save_stdout

test.fail_test(string.find(s, 'Main.py') == -1)
test.fail_test(string.find(s, 'print_help') == -1)
test.fail_test(string.find(s, '_main') == -1)
test.fail_test(string.find(s, 'option_parser.py') == -1)



scons_prof = test.workpath('scons2.prof')

test.run(arguments = "--profile %s" % scons_prof)

stats = pstats.Stats(scons_prof)
stats.sort_stats('time')

try:
    save_stdout = sys.stdout
    sys.stdout = StringIO.StringIO()

    stats.strip_dirs().print_stats()

    s = sys.stdout.getvalue()
finally:
    sys.stdout = save_stdout

test.fail_test(string.find(s, 'Main.py') == -1)
test.fail_test(string.find(s, '_main') == -1)
test.fail_test(string.find(s, 'FS.py') == -1)



scons_prof = test.workpath('scons3.prof')

test.run(arguments = "--profile %s --debug=memory -h" % scons_prof)
test.fail_test(string.find(test.stdout(), 'usage: scons [OPTION]') == -1)
test.fail_test(string.find(test.stdout(), 'Options:') == -1)

expect = 'Memory before reading SConscript files'
lines = string.split(test.stdout(), '\n')
memory_lines = filter(lambda l, e=expect: string.find(l, e) != -1, lines)

test.fail_test(len(memory_lines) != 1)

 

test.pass_test()
