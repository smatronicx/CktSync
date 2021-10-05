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
        config.Write(config_file)

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
        config.Write(config_file)
        # Create version history
        self.CreateVerHistory(cvpath)

    # Create version history file
    def CreateVerHistory(self, path):
        hist_file = os.path.join(path, const.CSYNCDIR, const.VERSIONFILE)
        config = CktSyncConfig()
        config.set(const.CONFIG_SECTION_CORE, const.VERSION_HEAD, str(0))
        config.set(const.CONFIG_SECTION_CORE, const.VERSION_LOCKED, str(False))
        config.Write(hist_file)

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
            config.Write(hist_file)
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
            config.Write(hist_file)
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
            config.Write(hist_file)
            return hist_file
        except:
            raise ValueError('Unable to lock {}->{}'.format(cellname, cellview))

    # Get cellview lock owner
    def GetCellviewLockOwner(self, libpath, cellname, cellview):
        cellpath = os.path.join(libpath, cellname)
        cvpath = os.path.join(cellpath, cellview)
        hist_file = os.path.join(cvpath, const.CSYNCDIR, const.VERSIONFILE)
        try:
            config = CktSyncConfig()
            config.Read(hist_file)
            islocked = config.get(const.CONFIG_SECTION_CORE, const.VERSION_LOCKED)
            if(islocked == str(False)):
                return None
            return config.get(const.CONFIG_SECTION_CORE, const.VERSION_LOCK_OWNER)

        except:
            raise ValueError('Failed to get owner of {}->{}'.format(cellname, cellview))



    # Create cell
    def CreateCell(self, libpath, cellname):
        # Check if cell is already managed
        cellpath = os.path.join(libpath, cellname)
        csync_dir = os.path.join(cellpath, '.csync')
        config_file = os.path.join(csync_dir, 'config')
        config = CktSyncConfig()
        ismanaged = False
        try:
            # Check if it is lib tag dir
            config.Read(config_file)
            dir_type = config.get('core', 'type')
            if(dir_type is not None and dir_type == 'cell'):
                ismanaged = True
        except:
            pass

        if(ismanaged == False):
            # Create config
            try:
                os.mkdir(csync_dir, mode=0o750)
            except:
                raise ValueError('Unable to add cell {}'.format(cellname))

            config.set('core','type','cell')
            config.Write(config_file)

            # Add cell in svn
            self.svnifc.Add(csync_dir)

        return ismanaged

    # Check cellview is managed
    def IsCellviewManaged(self, libpath, cellname, cellview):
        # Check if cellview is already managed
        cellpath = os.path.join(libpath, cellname, cellview)
        csync_dir = os.path.join(cellpath, '.csync')
        config_file = os.path.join(csync_dir, 'config')
        config = CktSyncConfig()
        ismanaged = False
        try:
            # Check if it is lib tag dir
            config.Read(config_file)
            dir_type = config.get('core', 'type')
            if(dir_type is not None and dir_type == 'cellview'):
                ismanaged = True
        except:
            pass

        return ismanaged

    # Create cellview
    def CreateCellview(self, libpath, cellname, cellview):
        # Check if cellview is already managed
        cellpath = os.path.join(libpath, cellname, cellview)
        csync_dir = os.path.join(cellpath, '.csync')
        config_file = os.path.join(csync_dir, 'config')
        config = CktSyncConfig()
        ismanaged = False
        try:
            # Check if it is lib tag dir
            config.Read(config_file)
            dir_type = config.get('core', 'type')
            if(dir_type is not None and dir_type == 'cellview'):
                ismanaged = True
        except:
            pass

        if(ismanaged == False):
            # Create config
            try:
                os.mkdir(csync_dir, mode=0o750)
                csync_lock = os.path.join(csync_dir, 'csync.lock')
                CktSyncUtil.touch(csync_lock)
                os.chmod(csync_lock, 0o640)

            except:
                raise ValueError('Unable to add cellview {} for cell {}'.format(cellview, cellname))

            config.set('core','type','cellview')
            config.Write(config_file)

            # Add cell in svn
            self.svnifc.Add(csync_dir)

        return ismanaged

    # Check if cellview is checkedout by user
    def GetCVLockOwner(self, libpath, cellname, cellview):
        # Check if cellview is already managed
        cellpath = os.path.join(libpath, cellname, cellview)
        csync_dir = os.path.join(cellpath, '.csync')
        csync_lock = os.path.join(csync_dir, 'csync.lock')
        lock_info = self.svnifc.InfoDict(csync_lock)
        lock_owner = lock_info.get('Lock Owner')
        if(lock_owner is None):
            # Not locked
            return None

        config = CktSyncConfig()
        try:
            # Check if it is lib tag dir
            config.Read(csync_lock)
            lock_owner = config.get('lock', 'user')
            return lock_owner
        except:
            return None

    # Set lock for cellview
    def SetCVLockOwner(self, libpath, cellname, cellview, user):
        # Check if cellview is already managed
        cellpath = os.path.join(libpath, cellname, cellview)
        csync_dir = os.path.join(cellpath, '.csync')
        csync_lock = os.path.join(csync_dir, 'csync.lock')
        config = CktSyncConfig()
        try:
            # Check if it is lib tag dir
            os.chmod(csync_lock, 0o640)
            config.Read(csync_lock)
            config.set('lock', 'user', user)
            config.Write(csync_lock)
            self.svnifc.Lock(csync_lock)
        except:
            raise ValueError('Failed to lock {}->{}'.format(cellname, cellview))


    # Remove lock for cellview
    def RemoveCVLockOwner(self, libpath, cellname, cellview):
        # Check if cellview is already managed
        cellpath = os.path.join(libpath, cellname, cellview)
        csync_dir = os.path.join(cellpath, '.csync')
        csync_lock = os.path.join(csync_dir, 'csync.lock')
        config = CktSyncConfig()
        try:
            # Check if it is lib tag dir
            config.Read(csync_lock)
            config.remove('lock')
            config.Write(csync_lock)
            self.svnifc.Unlock(csync_lock)
        except:
            raise ValueError('Failed to unlock {}->{}'.format(cellname, cellview))

    # Update history
    def UpdateHistory(self, user, libpath, cellname, cellview, cimsg):
        # Check if cellview is already managed
        cellpath = os.path.join(libpath, cellname, cellview)
        csync_dir = os.path.join(cellpath, '.csync')
        csync_history = os.path.join(csync_dir, 'history')
        config = CktSyncConfig()
        try:
            # Check if history file exists
            os.chmod(csync_history, 0o640)
            config.Read(csync_history)
        except:
            pass

        # Get current version
        try:
            cur_ver = config.get('current','version')
        except:
            cur_ver = 0

        cur_ver = str(int(cur_ver)+1)

        config.set('current','version', cur_ver)

        config.set(cur_ver, 'user', user)
        config.set(cur_ver, 'log', cimsg)
        config.Write(csync_history)
        return csync_history

    # Checkin cellview
    def CiCellview(self, user, libpath, cellname, cellview, cimsg):
        # Check if libpath is in worktag
        libtag = self.GetLibTag(libpath)
        if(libtag is None or libtag != 'work'):
            raise ValueError('Library {} is not in worktag'.format(libpath))

        # Create cell
        self.CreateCell(libpath, cellname)
        ismanaged = self.CreateCellview(libpath, cellname, cellview)
        do_commit = True
        if(ismanaged == True):
            # Check if user has lock
            lock_owner = self.GetCVLockOwner(libpath, cellname, cellview)
            if(lock_owner is None or lock_owner != user):
                do_commit = False

        cvpath = os.path.join(libpath, cellname, cellview)
        # If cdslck files exist do not checkin
        lock_files = glob.glob("*.cdslck*")
        if(len(lock_files) != 0):
            do_commit = False

        if(do_commit == True):
            histfile = self.UpdateHistory(user, libpath, cellname, cellview, cimsg)
            self.svnifc.Add(histfile)
            cvpath = os.path.join(libpath, cellname, cellview, '')
            self.svnifc.Add(cvpath)
            if(ismanaged == True):
                self.RemoveCVLockOwner(libpath, cellname, cellview)
            cellpath = os.path.join(libpath, cellname, '*')
            cellpaths = glob.glob(cellpath)
            cvpath = os.path.join(libpath, cellname)
            ci_item = [cvpath]
            for pathitem in cellpaths:
                if(os.path.isfile(pathitem)):
                    self.svnifc.Add(pathitem)
                    ci_item.append(pathitem)

            ci_item.append(os.path.join(libpath, cellname, cellview))
            self.svnifc.CommitItem(cimsg, ci_item)

            # Update file permission
            cvpath = os.path.join(libpath, cellname, cellview)
            CktSyncUtil.ChangePermission(cvpath, 0o750, 0o640)

        else:
            raise ValueError('Checkin failed for {}->{}'.format(cellname, cellview))

    # Checkout cellview
    def CoCellview(self, user, libpath, cellname, cellview):
        # Check if libpath is in worktag
        libtag = self.GetLibTag(libpath)
        if(libtag is None or libtag != 'work'):
            raise ValueError('Library {} is not in worktag'.format(libpath))

        # Create cell
        ismanaged = self.IsCellviewManaged(libpath, cellname, cellview)
        if(ismanaged == True):
            # Check if cellview is locked
            lock_owner = self.GetCVLockOwner(libpath, cellname, cellview)
            if(lock_owner is not None):
                raise ValueError('{}->{} is locked by {}'.format(cellname, cellview, lock_owner))

            self.SetCVLockOwner(libpath, cellname, cellview, user)

            # Update file permission
            cvpath = os.path.join(libpath, cellname, cellview)
            CktSyncUtil.ChangePermission(cvpath, 0o770, 0o660)

        else:
            raise ValueError('{}->{} is unmanaged'.format(cellname, cellview))
