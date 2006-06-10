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
This tests the feature of guessing the package name from the given metadata
projectname and version.

Also overriding this default package name is tested

Furthermore that targz is the default packager is tested.
"""

import os
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

tar = test.detect('TAR', 'tar')

if tar:
  #
  # TEST: default package name creation.
  #
  test.subdir('src')

  test.write( [ 'src', 'main.c' ], r"""
int main( int argc, char* argv[] )
{
  return 0;
}
  """)

  test.write('SConstruct', """
Program( 'src/main.c' )
Package( projectname = 'libfoo',
         version     = '1.2.3',
         source      = [ 'src/main.c', 'SConstruct' ] )
""")

  test.run(options="--debug=stacktrace", stderr = None)

  test.fail_test( not os.path.exists( 'libfoo-1.2.3.tar.gz' ) )

  #
  # TEST: overriding default package name.
  #

  test.write('SConstruct', """
Program( 'src/main.c' )
Package( projectname = 'libfoo',
         version     = '1.2.3',
         target      = 'src.tar.gz',
         source      = [ 'src/main.c', 'SConstruct' ] )
""")

  test.run(stderr = None)

  test.fail_test( not os.path.exists( 'src.tar.gz' ) )

  #
  # TEST: default package name creation with overriden packager.
  #

  test.write('SConstruct', """
Program( 'src/main.c' )
Package( projectname = 'libfoo',
         version     = '1.2.3',
         type        = 'tarbz2',
         source      = [ 'src/main.c', 'SConstruct' ] )
""")

  test.run(stderr = None)

  test.fail_test( not os.path.exists( 'libfoo-1.2.3.tar.bz2' ) )

test.pass_test()
