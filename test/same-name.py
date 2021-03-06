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
Make sure that we can build from a source file with the same basename as
the subdirectory in which it lives.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('bu')

test.write('SConstruct', """
env = Environment(CPPPATH = ['.'])
env.Program(source = ['foo.c', 'bu/bu.c'])
""")

test.write('foo.c', r"""
#include <stdio.h>
#include <stdlib.h>
#include <bu/bu.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        bu();
        printf("foo.c\n");
        exit (0);
}
""")

test.write(['bu', 'bu.h'], r"""
void bu(void);
""")

test.write(['bu', 'bu.c'], r"""
#include <stdio.h>
void
bu(void)
{
        printf("bu/bu.c\n");
}
""")

test.run(arguments = '.')

test.run(program = test.workpath("foo"), stdout ="""\
bu/bu.c
foo.c
""")

test.pass_test()
