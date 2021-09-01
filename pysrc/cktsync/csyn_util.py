#----------------
# This file is part of CktSync design manager
#----------------

import os
from .csyn_config import CktSyncConfig 

# Find root dir for a type
def FindTypeRoot(roottype):
  startdir = os.getcwd()
  while(True):
    rootdir = os.getcwd()
    csync_dir = os.path.join(rootdir, '.csync')
    config_file = os.path.join(csync_dir, 'config')
    config = CktSyncConfig()
    try:
      # Check if current dir is type root
      config.Read(config_file)
      dir_type = config.get('core', 'type')
      # Found root path, return
      if(dir_type is not None and dir_type == roottype):
        return rootdir
    except:
      pass
      
    # Move to upper folder
    try:
      os.chdir(os.path.pardir)
      # Check for system drive
      if(rootdir == os.getcwd()):
        break
    except:
      break
	
  # Not in root type tree
  raise ValueError('{} is not under {}.'.format(startdir, roottype))

# Update time stamp
def touch(fname, times=None):
  with open(fname, 'a'):
    os.utime(fname, times)

# Change permission for files and dir
def ChangePermission(path, dirmode, filemode):
  dirignore = ['.svn', '.csync']
  for root, dirs, files in os.walk(path):  
    dirs_tmp = []
    for item in dirs:
      if(item not in dirignore):
        os.chmod(os.path.join(root, item), dirmode)
        dirs_tmp.append(item)
    dirs[:] = dirs_tmp
    
    for item in files:
      os.chmod(os.path.join(root, item), filemode)
