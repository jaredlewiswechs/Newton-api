import os
print('cwd:', os.getcwd())
print('listing:', os.listdir('.'))
print('has foghorn dir?', os.path.isdir('foghorn'))
import sys
print('sys.path[0]:', sys.path[0])
try:
    import foghorn
    print('foghorn:', foghorn.__file__)
except Exception as e:
    print('import error:', e)
