#----------------
# This file is part of CktSync design manager
#----------------

import os
from .csyn_config import CktSyncConfig
from . import csyn_constants as const

# Get all parent directories
def GetParentDirs(path):
    rtnpaths = []
    dirpath = path
    while(True):
        dir_parent = os.path.dirname(dirpath)
        if(dir_parent == dirpath):
            break

        dirpath = dir_parent
        rtnpaths.append(dirpath)

    rtnpaths.reverse()
    return rtnpaths

# Get config file path in given path
def GetConfigPath(path):
    csync_dir = os.path.join(path, const.CSYNCDIR)
    config_file = os.path.join(csync_dir, const.CONFIGFILE)
    return config_file

# Find root dir for a type
def FindTypeRoot(roottype, startdir=None):
    if(startdir is None):
        startdir = os.getcwd()

    startdir = os.path.abspath(startdir)
    rootdir = startdir

    while(True):
        config_file = GetConfigPath(rootdir)
        config = CktSyncConfig()
        try:
            # Check if current dir is type root
            config.Read(config_file)
            ismatch = config.MatchCoreType(roottype)
            if(ismatch == True):
                return rootdir
        except:
            pass

        # Move to upper folder
        try:
            root_parent = os.path.dirname(rootdir)
            # Check for system drive
            if(root_parent == rootdir):
                break
            rootdir = root_parent
        except:
            break

    # Not in root type tree
    raise ValueError('{} is not under {}.'.format(startdir, roottype))
