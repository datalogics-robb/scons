# __COPYRIGHT__
#
# Benchmarks for testing various possible implementations of the
# env.__setitem__() method(s) in the src/engine/SCons/Environment.py
# module.

import os.path
import re
import sys
import timeit

# Utility Timing class and function from:
# ASPN: Python Cookbook : Timing various python statements
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/544297
#
# These wrap the basic timeit function to make it a little more
# convenient to do side-by-side tests of code.

class Timing:
    def __init__(self, name, num, init, statement):
        self.__timer = timeit.Timer(statement, init)
        self.__num   = num
        self.name    = name
        self.statement = statement
        self.__result  = None
        
    def timeit(self):
        self.__result = self.__timer.timeit(self.__num)
        
    def getResult(self):
        return self.__result

def times(num=1000000, reverse=False, init='', title='Results:', **statements):
    # time each statement
    timings = []
    for n, s in statements.iteritems():
        t = Timing(n, num, init, s)
        t.timeit()
        timings.append(t)
    
    print title
    timings.sort(key=Timing.getResult, reverse=reverse)
    for t in timings:
        #print "%s => %.3f s" % (t.name, t.getResult())
        print "    %.3f s   %s" % (t.getResult(), t.name)

# Import the necessary local SCons.* modules used by some of our
# alternative implementations below, first manipulating sys.path so
# we pull in the right local modules without forcing the user to set
# PYTHONPATH.

import __main__
script_dir = os.path.split(__main__.__file__)[0]
if script_dir:
    script_dir = script_dir + '/'
sys.path = [os.path.abspath(script_dir + '../src/engine')] + sys.path

import SCons.Errors
import SCons.Environment

is_valid_construction_var = SCons.Environment.is_valid_construction_var
global_valid_var = re.compile(r'[_a-zA-Z]\w*$')

# The classes with different __setitem__() implementations that we're
# going to horse-race.
#
# The base class (Environment) should contain *all* class initialization
# of anything that will be used by any of the competing sub-class
# implementations.  Each timing run will create an instance of the class,
# and all competing sub-classes should share the same initialization
# overhead so our timing focuses on just the __setitem__() performance.
#
# All subclasses should be prefixed with env_, in which case they'll be
# picked up automatically by the code below for testing.
#
# The env_Original subclass contains the original implementation (which
# actually had the is_valid_construction_var() function in SCons.Util
# originally).
#
# The other subclasses (except for env_Best) each contain *one*
# significant change from the env_Original implementation.  The doc string
# describes the change, and is what gets displayed in the final timing.
# The doc strings of these other subclasses are "grouped" informally
# by a prefix that kind of indicates what specific aspect of __setitem__()
# is being varied and tested.
#
# The env_Best subclass contains the "best practices" from each of
# the different "groups" of techniques tested in the other subclasses,
# and is where to experiment with different combinations of techniques.
# After we're done should be the one that shows up at the top of the
# list as we run our timings.

class Environment:
    _special_set = {
        'BUILDERS' : None,
        'SCANNERS' : None,
        'TARGET'   : None,
        'TARGETS'  : None,
        'SOURCE'   : None,
        'SOURCES'  : None,
    }
    _special_set_keys = _special_set.keys()
    _valid_var = re.compile(r'[_a-zA-Z]\w*$')
    def __init__(self, **kw):
        self._dict = kw

class env_Original(Environment):
    """Original __setitem__()"""
    def __setitem__(self, key, value):
        special = self._special_set.get(key)
        if special:
            special(self, key, value)
        else:
            if not SCons.Environment.is_valid_construction_var(key):
                raise SCons.Errors.UserError, "Illegal construction variable `%s'" % key
            self._dict[key] = value

class env_Global_is_valid(Environment):
    """is_valid_construction_var():  use a global function"""
    def __setitem__(self, key, value):
        special = self._special_set.get(key)
        if special:
            special(self, key, value)
        else:
            if not is_valid_construction_var(key):
                raise SCons.Errors.UserError, "Illegal construction variable `%s'" % key
            self._dict[key] = value

class env_Method_is_valid(Environment):
    """is_valid_construction_var():  use a method"""
    def is_valid_construction_var(self, varstr):
        """Return if the specified string is a legitimate construction
        variable.
        """
        return self._valid_var.match(varstr)

    def __setitem__(self, key, value):
        special = self._special_set.get(key)
        if special:
            special(self, key, value)
        else:
            if not self.is_valid_construction_var(key):
                raise SCons.Errors.UserError, "Illegal construction variable `%s'" % key
            self._dict[key] = value

class env_regex_attribute_is_valid(Environment):
    """is_valid_construction_var():  use a regex attribute"""
    def __setitem__(self, key, value):
        special = self._special_set.get(key)
        if special:
            special(self, key, value)
        else:
            if not self._valid_var.match(key):
                raise SCons.Errors.UserError, "Illegal construction variable `%s'" % key
            self._dict[key] = value

class env_global_regex_is_valid(Environment):
    """is_valid_construction_var():  use a global regex"""
    def __setitem__(self, key, value):
        special = self._special_set.get(key)
        if special:
            special(self, key, value)
        else:
            if not global_valid_var.match(key):
                raise SCons.Errors.UserError, "Illegal construction variable `%s'" % key
            self._dict[key] = value

class env_special_set_has_key(Environment):
    """_special_set.get():  use _special_set.has_key() instead"""
    def __setitem__(self, key, value):
        if self._special_set.has_key(key):
            self._special_set[key](self, key, value)
        else:
            if not SCons.Environment.is_valid_construction_var(key):
                raise SCons.Errors.UserError, "Illegal construction variable `%s'" % key
            self._dict[key] = value

class env_key_in_tuple(Environment):
    """_special_set.get():  use "key in tuple" instead"""
    def __setitem__(self, key, value):
        if key in ('BUILDERS', 'SCANNERS', 'TARGET', 'TARGETS', 'SOURCE', 'SOURCES'):
            self._special_set[key](self, key, value)
        else:
            if not SCons.Environment.is_valid_construction_var(key):
                raise SCons.Errors.UserError, "Illegal construction variable `%s'" % key
            self._dict[key] = value

class env_key_in_list(Environment):
    """_special_set.get():  use "key in list" instead"""
    def __setitem__(self, key, value):
        if key in ['BUILDERS', 'SCANNERS', 'TARGET', 'TARGETS', 'SOURCE', 'SOURCES']:
            self._special_set[key](self, key, value)
        else:
            if not SCons.Environment.is_valid_construction_var(key):
                raise SCons.Errors.UserError, "Illegal construction variable `%s'" % key
            self._dict[key] = value

class env_key_in_attribute(Environment):
    """_special_set.get():  use "key in attribute" instead"""
    def __setitem__(self, key, value):
        if key in self._special_set_keys:
            self._special_set[key](self, key, value)
        else:
            if not SCons.Environment.is_valid_construction_var(key):
                raise SCons.Errors.UserError, "Illegal construction variable `%s'" % key
            self._dict[key] = value

class env_try_except(Environment):
    """avoid is_valid_construction_var():  use try:-except:"""
    def __setitem__(self, key, value):
        special = self._special_set.get(key)
        if special:
            special(self, key, value)
        else:
            try:
                self._dict[key]
            except KeyError:
                if not SCons.Environment.is_valid_construction_var(key):
                    raise SCons.Errors.UserError, "Illegal construction variable `%s'" % key
            self._dict[key] = value

class env_not_has_key(Environment):
    """avoid is_valid_construction_var():  use not .has_key()"""
    def __setitem__(self, key, value):
        special = self._special_set.get(key)
        if special:
            special(self, key, value)
        else:
            if not self._dict.has_key(key) \
                and not SCons.Environment.is_valid_construction_var(key):
                    raise SCons.Errors.UserError, "Illegal construction variable `%s'" % key
            self._dict[key] = value

class env_Best_attribute(Environment):
    """Best __setitem__(), with an attribute"""
    def __setitem__(self, key, value):
        if key in self._special_set_keys:
            self._special_set[key](self, key, value)
        else:
            if not self._dict.has_key(key) \
               and not global_valid_var.match(key):
                    raise SCons.Errors.UserError, "Illegal construction variable `%s'" % key
            self._dict[key] = value

class env_Best_has_key(Environment):
    """Best __setitem__(), with has_key"""
    def __setitem__(self, key, value):
        if self._special_set.has_key(key):
            self._special_set[key](self, key, value)
        else:
            if not self._dict.has_key(key) \
               and not global_valid_var.match(key):
                    raise SCons.Errors.UserError, "Illegal construction variable `%s'" % key
            self._dict[key] = value

class env_Best_list(Environment):
    """Best __setitem__(), with a list"""
    def __setitem__(self, key, value):
        if key in ['BUILDERS', 'SCANNERS', 'TARGET', 'TARGETS', 'SOURCE', 'SOURCES']:
            self._special_set[key](self, key, value)
        else:
            if not self._dict.has_key(key) \
               and not global_valid_var.match(key):
                    raise SCons.Errors.UserError, "Illegal construction variable `%s'" % key
            self._dict[key] = value

# We'll use the names of all the env_* classes we find later to build
# the dictionary of statements to be timed, and the import statement
# that the timer will use to get at these classes.

env_class_names = [ n for n in locals().keys() if n.startswith('env_') ]

# This is *the* function that gets timed.  It will get called for the
# specified number of iterations for the cross product of the number of
# classes we're testing and the number of data sets (defined below).

iterations = 10000

def do_it(names, env_class):
    e = env_class()
    for key in names:
        e[key] = 1

# Build the list of "statements" that will be tested.  For each class
# we're testing, the doc string describing the class is the key, and
# the statement we test is a simple "doit(names, {class})" call.

statements = {}

for class_name in env_class_names:
    ec = eval(class_name)
    statements[ec.__doc__] = 'do_it(names, %s)' % class_name

# The common_imports string is used in the initialization of each
# test run.  The timeit module insulates the test snippets from the
# global namespace, so we have to import these explicitly from __main__.

common_import_variables = ['do_it'] + env_class_names

common_imports = """
from __main__ import %s
""" % ', '.join(common_import_variables)

# The test data (lists of variable names) that we'll use for the runs.

same_variable_names = ['XXX'] * 100
uniq_variable_names = [ 'X%02d' % i for i in xrange(100) ]
mixed_variable_names = same_variable_names[:50] + uniq_variable_names[:50]

# Lastly, put it all together...

times(num = iterations,
      title = 'Results for re-adding an existing variable name 100 times:',
      init = common_imports + """
from __main__ import same_variable_names as names
""",
      **statements
)

times(num = iterations,
      title = 'Results for adding 100 variable names, 50 existing and 50 new:',
      init = common_imports + """
from __main__ import mixed_variable_names as names
""",
      **statements
)

times(num = iterations,
      title = 'Results for adding 100 new, unique variable names:',
      init = common_imports + """
from __main__ import uniq_variable_names as names
""",
      **statements
)