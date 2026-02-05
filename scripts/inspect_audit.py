from core import audit
import os
print('LOG_FILE=', audit.LOG_FILE)
print('exists dir?', os.path.isdir(os.path.dirname(audit.LOG_FILE)))
print('files:', os.listdir(os.path.dirname(audit.LOG_FILE)))
