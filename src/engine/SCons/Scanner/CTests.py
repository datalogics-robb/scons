#
# Copyright (c) 2001 Steven Knight
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

import TestCmd
import SCons.Scanner.C
import unittest
import sys
import os
import os.path

test = TestCmd.TestCmd(workdir = '')

os.chdir(test.workpath(''))

# create some source files and headers:

test.write('f1.cpp',"""
#include \"f1.h\"
#include <f2.h>

int main()
{
   return 0;
}
""")

test.write('f2.cpp',"""
#include \"d1/f1.h\"
#include <d2/f1.h>
#include \"f1.h\"
#include <f4.h>

int main()
{
   return 0;
}
""")

test.write('f3.cpp',"""
#include \t "f1.h"
   \t #include "f2.h"
#   \t include "f3.h"

#include \t <d1/f1.h>
   \t #include <d1/f2.h>
#   \t include <d1/f3.h>

// #include "never.h"

const char* x = "#include <never.h>"

int main()
{
   return 0;
}
""")


# for Emacs -> "

test.subdir('d1', ['d1', 'd2'])

headers = ['f1.h','f2.h', 'f3.h', 'fi.h', 'fj.h', 'never.h',
           'd1/f1.h', 'd1/f2.h', 'd1/f3.h', 'd1/fi.h', 'd1/fj.h',
           'd1/d2/f1.h', 'd1/d2/f2.h', 'd1/d2/f3.h',
           'd1/d2/f4.h', 'd1/d2/fi.h', 'd1/d2/fj.h']

for h in headers:
    test.write(h, " ")

test.write('f2.h',"""
#include "fi.h"
""")

test.write('f3.h',"""
#include <fj.h>
""")

# define some helpers:

class DummyEnvironment:
    def __init__(self, listCppPath):
        self.path = listCppPath
        
    def Dictionary(self, *args):
        if not args:
            return { 'CPPPATH': self.path }
        elif len(args) == 1 and args[0] == 'CPPPATH':
            return self.path
        else:
            raise KeyError, "Dummy environment only has CPPPATH attribute."

def deps_match(self, deps, headers):
    deps = map(os.path.normpath, map(str, deps))
    headers = map(os.path.normpath, map(test.workpath, headers))
    deps.sort()
    headers.sort()
    self.failUnless(deps == headers, "expect %s != scanned %s" % (headers, deps))

# define some tests:

class CScannerTestCase1(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([])
        s = SCons.Scanner.C.CScan()
        deps = s.instance(env).scan(test.workpath('f1.cpp'), env)
	headers = ['f1.h', 'f2.h', 'fi.h']
        deps_match(self, deps, headers)

class CScannerTestCase2(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([test.workpath("d1")])
        s = SCons.Scanner.C.CScan()
        deps = s.instance(env).scan(test.workpath('f1.cpp'), env)
        headers = ['f1.h', 'd1/f2.h']
        deps_match(self, deps, headers)

class CScannerTestCase3(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([test.workpath("d1")])
        s = SCons.Scanner.C.CScan()
        deps = s.instance(env).scan(test.workpath('f2.cpp'), env)
        headers = ['f1.h', 'd1/f1.h', 'd1/d2/f1.h']
        deps_match(self, deps, headers)

class CScannerTestCase4(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([test.workpath("d1"), test.workpath("d1/d2")])
        s = SCons.Scanner.C.CScan()
        deps = s.instance(env).scan(test.workpath('f2.cpp'), env)
        headers =  ['f1.h', 'd1/f1.h', 'd1/d2/f1.h', 'd1/d2/f4.h']
        deps_match(self, deps, headers)
        
class CScannerTestCase5(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([])
        s = SCons.Scanner.C.CScan()
        deps = s.instance(env).scan(test.workpath('f3.cpp'), env)
        headers =  ['f1.h', 'f2.h', 'f3.h', 'fi.h', 'fj.h',
                    'd1/f1.h', 'd1/f2.h', 'd1/f3.h']
        deps_match(self, deps, headers)

class CScannerTestCase6(unittest.TestCase):
    def runTest(self):
        env1 = DummyEnvironment([test.workpath("d1")])
        env2 = DummyEnvironment([test.workpath("d1/d2")])
        s = SCons.Scanner.C.CScan()
	s1 = s.instance(env1)
	s2 = s.instance(env2)
	s3 = s.instance(env1)
	assert not s1 is s2
	assert s1 is s3
        deps1 = s1.scan(test.workpath('f1.cpp'), None)
        deps2 = s2.scan(test.workpath('f1.cpp'), None)
        headers1 =  ['f1.h', 'd1/f2.h']
        headers2 =  ['f1.h', 'd1/d2/f2.h']
        deps_match(self, deps1, headers1)
        deps_match(self, deps2, headers2)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(CScannerTestCase1())
    suite.addTest(CScannerTestCase2())
    suite.addTest(CScannerTestCase3())
    suite.addTest(CScannerTestCase4())
    suite.addTest(CScannerTestCase5())
    suite.addTest(CScannerTestCase6())
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)
