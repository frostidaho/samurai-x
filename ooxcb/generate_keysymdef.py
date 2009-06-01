from __future__ import with_statement

import re

KEYSYMDEF = '/usr/include/X11/keysymdef.h'
PATTERN = '^#define *XK_([^ ]+) *([0-9xA-Za-z]+).*$'
regex = re.compile(PATTERN, re.MULTILINE)

keysyms = {}

with open(KEYSYMDEF, 'r') as f:
    for match in regex.finditer(f.read()):
        keysyms[match.group(1)] = int(match.group(2), base=16)

names = dict((v, k) for k, v in keysyms.iteritems())

def get_value(v):
    if isinstance(v, int):
        return hex(v)
    else:
        return repr(v)

def print_dict(name, dic):
    print '%s = {' % name
    for key, value in dic.iteritems():
        print '    %s: %s,' % (get_value(key), get_value(value))
    print '}'

print '# autogenerated from %s' % KEYSYMDEF
print
print_dict('keysyms', keysyms)
print_dict('names', names)
