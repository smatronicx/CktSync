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
            os.chmod(item, filemode)
        except:
            failed_paths.append(os.path.join(path, item))

    # Raise error
    if(len(failed_paths) != 0):
        raise ValueError('Failed to change permission for {}'.format(failed_paths))

# Link all files and dirs in from srcpath to dstpath
def CreatePathLink(srcpath, dstpath, ignorelist=[], relpath=False):
    failed_paths = []
    dirs, files = ScanDir(srcpath)
    files.extend(dirs)
    for srcfilepath in files:
        filename = os.path.basename(srcfilepath)
        dstfilepath = os.path.join(dstpath, filename)
        exists = os.path.exists(dstfilepath)
        # Check if we should create link to the file in dstpath
        createlink = True
        if(exists == True):
            createlink = False
            failed_paths.append(srcfilepath)

        if(createlink == True):
            if(filename not in ignorelist):
                try:
                    if(relpath == True):
                        srcfilepath = os.path.relpath(srcfilepath, dstpath)
                    os.symlink(srcfilepath, dstfilepath)
                except:
                    failed_paths.append(srcfilepath)

    # Raise error
    if(len(failed_paths) != 0):
        raise ValueError('Failed to create links for {}'.format(failed_paths))

# Remove links from path
def RemovePathLink(path, ignorelist=[]):
    failed_paths = []
    dirs, files = ScanDir(path)
    files.extend(dirs)
    for filepath in files:
        filename = os.path.basename(filepath)
        if(filename not in ignorelist):
            islink = os.path.islink(filepath)
            if(islink == True):
                try:
                    os.unlink(filepath)
                except:
                    failed_paths.append(filepath)

    # Raise error
    if(len(failed_paths) != 0):
        raise ValueError('Failed to create links for {}'.format(failed_paths))

# Remove directory
def DeleteDir(path, keeproot=False):
    failed_paths = []
    # Remove links
    try:
        RemovePathLink(path)
    except:
        failed_paths.append(path)

    dirs, files = ScanDir(path)
    # Remove dirs
    for item in dirs:
        try:
            DeleteDir(item)
        except:
            failed_paths.append(item)

    # Remove files
    for item in files:
        try:
            os.remove(item)
        except:
            failed_paths.append(item)

    # Remove Path
    if(keeproot == False):
        try:
            os.rmdir(path)
        except:
            failed_paths.append(path)

    # Raise error
    if(len(failed_paths) != 0):
        raise ValueError('Failed to change permission for {}'.format(failed_paths))

# Remove content of directory
def EmptyDir(path):
    DeleteDir(path, keeproot=True)
