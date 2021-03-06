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

import unittest
import SCons.Errors
import SCons.Script.Main

# Unit tests of various classes within SCons.Script.Main.py.
#
# Most of the tests of this functionality are actually end-to-end scripts
# in the test/ hierarchy.
#
# This module is for specific bits of functionality that we can test
# more effectively here, instead of in an end-to-end test that would
# have to reach into SCons.Script.Main for various classes or other bits
# of private functionality.

class SConscriptSettableOptionsTestCase(unittest.TestCase):

    def setUp(self):
        class fake_option:
            pass
        option = fake_option()
        self.ssoptions = SCons.Script.Main.SConscriptSettableOptions(option)

    def test_get(self):
        """Test trying to get an option that is not SConscript-gettable"""
        try:
            self.ssoptions.get('memoizer')
        except SCons.Errors.UserError:
            pass
        else:
            raise ValueError, "expected a UserError trying to get('memoizer')"

    def test_set(self):
        """Test trying to set an option that is not SConscript-settable"""
        try:
            self.ssoptions.set('count', 1)
        except SCons.Errors.UserError:
            pass
        else:
            raise ValueError, "expected a UserError trying to set('count', 1)"



if __name__ == "__main__":
    suite = unittest.TestSuite()
    tclasses = [ SConscriptSettableOptionsTestCase, ]
    for tclass in tclasses:
        names = unittest.getTestCaseNames(tclass, 'test_')
        suite.addTests(map(tclass, names))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
