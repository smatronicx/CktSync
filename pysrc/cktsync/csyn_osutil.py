#----------------
# This file is part of CktSync design manager
#----------------

import os
import shutil
from . import csyn_constants as const

# Update time stamp
def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

# Make dir
def mkdir(dirpath, exists=False, **kwargs):
    # Try to make directory
    # If "exists" flag is set to true, raise Exception
    if(os.path.exists(dirpath) == True):
        if(exists == True):
            raise FileExistsError

    else:
        os.mkdir(dirpath, **kwargs)

# Copy only files from src to dst
def CopyFiles(srcpath, dstpath, copylink=False, overwrite=True):
    _,files = ScanDir(srcpath)
    for srcfilepath in files:
        filename = os.path.basename(srcfilepath)
        dstfilepath = os.path.join(dstpath, filename)
        islink = os.path.islink(srcfilepath)
        exists = os.path.exists(dstfilepath)
        # Check if we should copy the file to dstpath
        docopy = True
        if(copylink == False and islink == True):
            docopy = False
        if(exists == True):
            if(overwrite == False):
                docopy = False
            else:
                os.chmod(dstfilepath, 0o640)

        if(docopy == True):
            shutil.copyfile(srcfilepath, dstfilepath)

# Copy a directory from src to dst
def CopyDirectory(srcpath, dstpath, copylink=False, overwrite=True, ignorelist=[]):
    mkdir(dstpath, mode=0o750)
    if(overwrite == True):
        os.chmod(dstpath, 0o750)
        
    CopyFiles(srcpath, dstpath, copylink=copylink, overwrite=overwrite)
    dirs,_ = ScanDir(srcpath)
    for srcdirpath in dirs:
        dirname = os.path.basename(srcdirpath)
        dstdirpath = os.path.join(dstpath, dirname)
        islink = os.path.islink(srcdirpath)
        # Check if we should copy the dir to dstpath
        docopy = True
        if(copylink == False and islink == True):
            docopy = False
        if(dirname in ignorelist):
            docopy = False

        if(docopy == True):
            CopyDirectory(srcdirpath, dstdirpath, copylink=copylink, overwrite=overwrite, ignorelist=ignorelist)

# Get files and dirs into 2 lists for a path
def ScanDir(path):
    files = []
    dirs = []
    path_items = os.listdir(path)
    for item in path_items:
        item = os.path.join(path, item)
        if(os.path.isfile(item)):
            files.append(item)
        else:
            dirs.append(item)

    return dirs, files

# Change permission for files and dir
def ChangePermission(path, dirmode=0o750, filemode=0o640, ignorelist = []):
    failed_paths = []
    for root, dirs, files in os.walk(path):
        dirs_tmp = []
        for item in dirs:
            if(item not in ignorelist):
                try:
                    os.chmod(os.path.join(root, item), dirmode)
                except:
                    failed_paths.append(os.path.join(root, item))
                dirs_tmp.append(item)

        dirs[:] = dirs_tmp

        for item in files:
            try:
                os.chmod(os.path.join(root, item), filemode)
            except:
                failed_paths.append(os.path.join(root, item))

    # Raise error
    if(len(failed_paths) != 0):
        raise ValueError('Failed to change permission for {}'.format(failed_paths))

# Change permission of files in path
def ChangeFilePermission(path, filemode=0o640):
    failed_paths = []
    _, files = ScanDir(path)

    for item in files:
        try:
            os.chmod(os.path.join(path, item), filemode)
        except:
            failed_paths.append(os.path.join(path, item))

    # Raise error
    if(len(failed_paths) != 0):
        raise ValueError('Failed to change permission for {}'.format(failed_paths))
