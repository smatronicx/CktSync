#----------------
# This file is part of CktSync design manager
#----------------

import os
from .csyn_svn import CktSyncSvn
from .csyn_config import CktSyncConfig
from . import csyn_util as CktSyncUtil
from . import csyn_osutil as OsUtil
from . import csyn_constants as const
import glob


# Class for CktSync design management interface
class CktSyncDMBase():
    # Initialize
    def __init__(self, repo, user, passwd):
        self.svnifc = CktSyncSvn(repo, user, passwd)

    # Check if the lib path is managed by cktsync
    def ManagedPath(self, path, type):
        config_file = CktSyncUtil.GetConfigPath(path)
        config = CktSyncConfig()
        ismanaged = False
        try:
            # Check if it is managed path of given type
            config.Read(config_file)
            ismanaged = config.MatchCoreType(type)
        except:
            ismanaged = False

        return ismanaged, config

    # Get lib tag
    def GetLibTag(self, libpath):
        ismanaged, config = self.ManagedPath(libpath, const.TYPE_TAG)
        if(ismanaged == False):
            return None

        tag_type = config.get(const.TYPE_TAG, const.CONFIG_TYPE)

        return tag_type

    # Get tag path
    def GetTagPath(self, libpath, tagname):
        try:
            libroot = CktSyncUtil.FindTypeRoot(const.TYPE_LIB, startdir=libpath)
        except:
            raise ValueError('{} is not a valid library'.format(libpath))

        # Get all dirs in libroot
        dirs,_ = OsUtil.ScanDir(libroot)
        for dirname in dirs:
            tag_type = self.GetLibTag(dirname)
            dirname = os.path.basename(dirname)
            if(tag_type is None):
                # Not a valid tag
                pass
            elif(tag_type == tagname):
                # Internal tag
                return dirname
            elif(dirname == tagname):
                # Tagname same as dirname
                return dirname

        raise ValueError('tag {} does not exist in libroot {}'.format(tagname, libroot))

    # Get all tags
    def GetAllTags(self, libpath):
        try:
            libroot = CktSyncUtil.FindTypeRoot(const.TYPE_LIB, startdir=libpath)
        except:
            raise ValueError('{} is not a valid library'.format(libpath))

        tags = []
        # Get all dirs in libroot
        dirs,_ = OsUtil.ScanDir(libroot)
        for dirname in dirs:
            tag_type = self.GetLibTag(dirname)
            if(tag_type is not None):
                # Add tag name
                tags.append(os.path.basename(dirname))

        # Sort
        tags.sort()
        return tags

    # Check if cell existes in a tag
    def IsCellInTag(self, libroot, tag, cellname):
        # Get tag path and type
        tagpath = self.GetTagPath(libroot, tag)
        libpath = os.path.join(libroot, tagpath)
        tagname = self.GetLibTag(libpath)
        cellpath = os.path.join(libpath, cellname)
        # Check if cell is managed by cktsync
        ismanaged, config = self.ManagedPath(cellpath, const.TYPE_CELL)
        return ismanaged

    # Check if cellview existes in a tag
    def IsCellviewInTag(self, libroot, tag, cellname, cellview):
        # Get tag path and type
        tagpath = self.GetTagPath(libroot, tag)
        libpath = os.path.join(libroot, tagpath)
        tagname = self.GetLibTag(libpath)
        cellviewpath = os.path.join(libpath, cellname, cellview)
        # Check if cell is managed by cktsync
        ismanaged, config = self.ManagedPath(cellviewpath, const.TYPE_CELLVIEW)
        return ismanaged

    # Copy cell from one tag to another
    def CopyCell(self, libroot, cellname, srctag, dsttag):
        # Get tag path and type
        tagpath = self.GetTagPath(libroot, srctag)
        srclibpath = os.path.join(libroot, tagpath)
        tagpath = self.GetTagPath(libroot, dsttag)
        dstlibpath = os.path.join(libroot, tagpath)
        srccellpath = os.path.join(srclibpath, cellname)
        dstcellpath = os.path.join(dstlibpath, cellname)

        # Check if cell exists and managed
        ismanaged = self.IsCellInTag(libroot, srctag, cellname)
        if(ismanaged == False):
            raise ValueError('{} in {} is not managed by CktSync.'.format(cellname, srctag))

        # Create cell and copy
        try:
            # Create cell in totag
            OsUtil.mkdir(dstcellpath, mode=0o750)
            # copy all files to new cell
            OsUtil.CopyFiles(srccellpath, dstcellpath, copylink=False, overwrite=True)
            # Copy CSYNCDIR to dstpath
            srccsync = os.path.join(srccellpath, const.CSYNCDIR)
            dstcsync = os.path.join(dstcellpath, const.CSYNCDIR)
            OsUtil.CopyDirectory(srccsync, dstcsync, copylink=False, overwrite=True, ignorelist=['.svn'])

        except:
            raise ValueError('Failed to copy {} for {} to {}'.format(cellname, srctag, dsttag))

        # Fix file permissions
        try:
            OsUtil.ChangeFilePermission(dstcellpath, filemode=0o440)
            OsUtil.ChangePermission(dstcsync, dirmode=0o750, filemode=0o440)
        except:
            raise ValueError('Failed to copy {} from {} to {}'.format(cellname, srctag, dsttag))

    # Add cell to svn in a tag
    def SVNAddCell(self, libroot, cellname, tag):
        # Get tag path and type
        tagpath = self.GetTagPath(libroot, tag)
        libpath = os.path.join(libroot, tagpath)
        cellpath = os.path.join(libpath, cellname)
        csyncpath = os.path.join(cellpath, const.CSYNCDIR)

        # Add cell, files and CSYNCDIR
        try:
            self.svnifc.AddSingle(cellpath)
            self.svnifc.AddAll(csyncpath)
            _,files = OsUtil.ScanDir(cellpath)
            for item in files:
                self.svnifc.Add(item)
            msg = 'Added {}->{}->{}'.format(libroot, tag, cellname)
            self.svnifc.CommitSingle(msg, cellpath)
            files.append(csyncpath)
            self.svnifc.CommitItem(msg, files)
        except:
            raise ValueError('Failed to add {}->{}->{} to svn'.format(libroot, tag, cellname))

    # Copy cellview from one tag to another
    def CopyCellview(self, libroot, cellname, cellview, srctag, dsttag):
        # Get tag path and type
        tagpath = self.GetTagPath(libroot, srctag)
        srclibpath = os.path.join(libroot, tagpath)
        tagpath = self.GetTagPath(libroot, dsttag)
        dstlibpath = os.path.join(libroot, tagpath)
        srccellpath = os.path.join(srclibpath, cellname)
        dstcellpath = os.path.join(dstlibpath, cellname)

        # Copy cell first
        self.CopyCell(libroot, cellname, srctag, dsttag)

        # Check if cellview exists and managed
        ismanaged = self.IsCellviewInTag(libroot, srctag, cellname, cellview)
        if(ismanaged == False):
            raise ValueError('{}->{} in {} is not managed by CktSync.'.format(cellname, cellview, srctag))

        # Copy cellview
        try:
            srccellview = os.path.join(srccellpath, cellview)
            dstcellview = os.path.join(dstcellpath, cellview)
            OsUtil.CopyDirectory(srccellview, dstcellview, copylink=False, overwrite=True, ignorelist=['.svn'])

        except:
            raise ValueError('Failed to copy {}->{} for {} to {}'.format(cellname, cellview, srctag, dsttag))

        # Fix file permissions
        try:
            OsUtil.ChangePermission(dstcellview, dirmode=0o750, filemode=0o440)
        except:
            raise ValueError('Failed to copy {}->{} for {} to {}'.format(cellname, cellview, srctag, dsttag))

    # Add cell to svn in a tag
    def SVNAddCellview(self, libroot, cellname, cellview, tag):
        # Get tag path and type
        tagpath = self.GetTagPath(libroot, tag)
        libpath = os.path.join(libroot, tagpath)
        cellpath = os.path.join(libpath, cellname)
        cvpath = os.path.join(cellpath, cellview)

        # Add cell first
        self.SVNAddCell(libroot, cellname, tag)
        # Add cellview
        try:
            self.svnifc.AddAll(cvpath)
            msg = 'Added {}->{}->{}->{}'.format(libroot, tag, cellname, cellview)
            self.svnifc.CommitItem(msg, [cvpath])
        except:
            raise ValueError('Failed to add {}->{}->{}->{} to svn'.format(libroot, tag, cellname, cellview))

    # Convert cell to managed cell
    def ManageCell(self, libroot, cellname, tag):
        # Get tag path and type
        tagpath = self.GetTagPath(libroot, tag)
        libpath = os.path.join(libroot, tagpath)
        cellpath = os.path.join(libpath, cellname)

        # Check if cell exists
        if(os.path.exists(cellpath) == False):
            raise ValueError('{} does not exists in {}'.format(cellname, libpath))

        ismanaged = self.IsCellInTag(libroot, tag, cellname)
        if(ismanaged == True):
            return

        # Make CSYNCDIR
        config_file = CktSyncUtil.CreateConfig(cellpath)
        config = CktSyncConfig()
        config.SetCoreType(const.TYPE_CELL)
        config.Write(config_file, makero=True)

    # Convert cellview to managed cellview
    def ManageCellview(self, libroot, cellname, cellview, tag):
        # Get tag path and type
        tagpath = self.GetTagPath(libroot, tag)
        libpath = os.path.join(libroot, tagpath)
        cellpath = os.path.join(libpath, cellname)
        cvpath = os.path.join(cellpath, cellview)

        # Check if cell exists
        if(os.path.exists(cvpath) == False):
            raise ValueError('{} does not exists in {}'.format(cellview, cellpath))

        ismanaged = self.IsCellviewInTag(libroot, tag, cellname, cellview)
        if(ismanaged == True):
            return

        # Make CSYNCDIR
        config_file = CktSyncUtil.CreateConfig(cvpath)
        config = CktSyncConfig()
        config.SetCoreType(const.TYPE_CELLVIEW)
        config.Write(config_file, makero=True)
        # Create version history
        self.CreateVerHistory(cvpath)

    # Create version history file
    def CreateVerHistory(self, path):
        hist_file = os.path.join(path, const.CSYNCDIR, const.VERSIONFILE)
        config = CktSyncConfig()
        config.set(const.CONFIG_SECTION_CORE, const.VERSION_HEAD, str(0))
        config.set(const.CONFIG_SECTION_CORE, const.VERSION_LOCKED, str(False))
        config.Write(hist_file,  makero=True)

    # Update the version file
    def UpdateVerHistory(self, path, user, msg):
        hist_file = os.path.join(path, const.CSYNCDIR, const.VERSIONFILE)
        try:
            config = CktSyncConfig()
            config.Read(hist_file)
            head = config.get(const.CONFIG_SECTION_CORE, const.VERSION_HEAD)
            head = str(int(head)+1)
            config.set(const.CONFIG_SECTION_CORE, const.VERSION_HEAD, head)
            config.set(head, const.VERSION_USER, user)
            config.set(head, const.VERSION_LOG, msg)
            config.Write(hist_file, force=True, makero=True)
        except:
            raise ValueError('Unable to update version info for {}'.format(path))

    # Lock cell view for edit
    def LockCellview(self, libpath, cellname, cellview, user):
        # Check if cellview is already lock
        owner = self.GetCellviewLockOwner(libpath, cellname, cellview)
        if(owner is not None):
            raise ValueError('{}->{}->{} is locked by {}'.format(libpath, cellname, cellview, owner))

        # lock the cellview
        cellpath = os.path.join(libpath, cellname)
        cvpath = os.path.join(cellpath, cellview)
        hist_file = os.path.join(cvpath, const.CSYNCDIR, const.VERSIONFILE)
        try:
            self.svnifc.Lock(hist_file)
            config = CktSyncConfig()
            config.Read(hist_file)
            config.set(const.CONFIG_SECTION_CORE, const.VERSION_LOCKED, str(True))
            config.set(const.CONFIG_SECTION_CORE, const.VERSION_LOCK_OWNER, user)
            config.Write(hist_file, force=True, makero=True)
        except:
            raise ValueError('Unable to lock {}->{}'.format(cellname, cellview))

    # Unlock cell view
    def UnlockCellview(self, libpath, cellname, cellview, user):
        # Check if cellview is already lock
        owner = self.GetCellviewLockOwner(libpath, cellname, cellview)
        if(owner != user):
            raise ValueError('{}->{}->{} is locked by {}'.format(libpath, cellname, cellview, owner))

        # lock the cellview
        cellpath = os.path.join(libpath, cellname)
        cvpath = os.path.join(cellpath, cellview)
        hist_file = os.path.join(cvpath, const.CSYNCDIR, const.VERSIONFILE)
        try:
            config = CktSyncConfig()
            config.Read(hist_file)
            config.set(const.CONFIG_SECTION_CORE, const.VERSION_LOCKED, str(False))
            config.unset(const.CONFIG_SECTION_CORE, const.VERSION_LOCK_OWNER)
            config.Write(hist_file, force=True, makero=True)
            return hist_file
        except:
            raise ValueError('Unable to lock {}->{}'.format(cellname, cellview))

    # Get cellview lock owner
    def GetCellviewLockOwner(self, libpath, cellname, cellview):
        cellpath = os.path.join(libpath, cellname)
        cvpath = os.path.join(cellpath, cellview)
        hist_file = os.path.join(cvpath, const.CSYNCDIR, const.VERSIONFILE)
        lock_owner = self.svnifc.LockOwner(hist_file)
        if(lock_owner is None):
            # Not locked
            return None

        try:
            config = CktSyncConfig()
            config.Read(hist_file)
            islocked = config.get(const.CONFIG_SECTION_CORE, const.VERSION_LOCKED)
            if(islocked == str(False)):
                return None
            return config.get(const.CONFIG_SECTION_CORE, const.VERSION_LOCK_OWNER)

        except:
            raise ValueError('Failed to get owner of {}->{}'.format(cellname, cellview))
