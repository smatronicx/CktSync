#----------------
# This file is part of CktSync design manager
#----------------

import os
from .csyn_svn import CktSyncSvn
from .csyn_config import CktSyncConfig
from .csyn_dmbase import CktSyncDMBase
from . import csyn_util as CktSyncUtil
from . import csyn_osutil as OsUtil
from . import csyn_constants as const


# Class for CktSync design management interface
class CktSyncDM(CktSyncDMBase):
    # Initialize
    def __init__(self, repo, user, passwd):
        super().__init__(repo, user, passwd)

    # Checkin Cellview. Cells can be checkin only from work tag
    def CiCellview(self, user, libpath, cellname, cellview, cimsg):
        # Check for work tag
        libroot = CktSyncUtil.FindTypeRoot(const.TYPE_LIB, startdir=libpath)
        tagname = self.GetLibTag(libpath)

        if(tagname != const.TAG_WORK):
            raise ValueError('{} is not in work tag'.format(libpath))

        # Check if cell and cellview are present in latest
        tagpath = self.GetTagPath(libroot, const.TAG_LATEST)
        libpath_latest = os.path.join(libroot, tagpath)
        ismanaged = self.IsCellInTag(libroot, const.TAG_LATEST, cellname)
        if(ismanaged == False):
            # ManageCell
            self.ManageCell(libroot, cellname, const.TAG_WORK)

        ismanaged  = self.IsCellviewInTag(libroot, const.TAG_LATEST, cellname, cellview)
        firstci = False
        if(ismanaged == False):
            # Manage cellview
            self.ManageCellview(libroot, cellname, cellview, const.TAG_WORK)
            firstci = True

        else:
            # Check if the cell is checkedout by user
            owner = self.GetCellviewLockOwner(libpath_latest, cellname, cellview)
            if(owner is None):
                raise ValueError('{}->{} is not checkedout'.format(cellname, cellview))
            if(owner != user):
                raise ValueError('{}->{} is locked by {}'.format(cellname, cellview, owner))

        # Update version
        cellpath = os.path.join(libpath, cellname)
        cvpath = os.path.join(cellpath, cellview)
        self.UpdateVerHistory(cvpath, user, cimsg)
        # Copy cellview to latest
        self.CopyCellview(libroot, cellname, cellview, const.TAG_WORK, const.TAG_LATEST)
        # Unlock the cellview and add to snv
        if(firstci == False):
            hist_file = self.UnlockCellview(libpath_latest, cellname, cellview, user)
        self.SVNAddCellview(libroot, cellname, cellview, const.TAG_LATEST)
        # Update cell in work tag
        self.UpdateCellview(libroot, cellname, cellview, const.TAG_WORK)

    # Checkin Cellview. Cells can be checkout only from work tag
    def CoCellview(self, user, libpath, cellname, cellview):
        # Check for work tag
        libroot = CktSyncUtil.FindTypeRoot(const.TYPE_LIB, startdir=libpath)
        tagname = self.GetLibTag(libpath)

        if(tagname != const.TAG_WORK):
            raise ValueError('{} is not in work tag'.format(libpath))

        # Check if cell and cellview are present in latest
        tagpath = self.GetTagPath(libroot, const.TAG_LATEST)
        libpath_latest = os.path.join(libroot, tagpath)
        ismanaged = self.IsCellInTag(libroot, const.TAG_LATEST, cellname)
        if(ismanaged == False):
            raise ValueError('{}->{} is not in managed'.format(cellname, cellview))

        ismanaged  = self.IsCellviewInTag(libroot, const.TAG_LATEST, cellname, cellview)
        if(ismanaged == False):
            raise ValueError('{}->{} is not in managed'.format(cellname, cellview))

        else:
            # Check if the cell is checkedout by user
            owner = self.GetCellviewLockOwner(libpath_latest, cellname, cellview)
            if(owner is not None):
                raise ValueError('{}->{} is locked by {}'.format(cellname, cellview, owner))

        # Lock cellview
        self.LockCellview(libpath_latest, cellname, cellview, user)
        # Empty the cellview in worktag
        self.EmptyCellview(libroot, cellname, cellview, const.TAG_WORK)

    # Cancel checkout of Cellview. Cells can be cancelled only from work tag
    def CancelCoCellview(self, user, libpath, cellname, cellview):
        # Check for work tag
        libroot = CktSyncUtil.FindTypeRoot(const.TYPE_LIB, startdir=libpath)
        tagname = self.GetLibTag(libpath)

        if(tagname != const.TAG_WORK):
            raise ValueError('{} is not in work tag'.format(libpath))

        # Check if cell and cellview are present in latest
        tagpath = self.GetTagPath(libroot, const.TAG_LATEST)
        libpath_latest = os.path.join(libroot, tagpath)
        ismanaged = self.IsCellInTag(libroot, const.TAG_LATEST, cellname)
        if(ismanaged == False):
            raise ValueError('{} is not managed'.format(cellname))

        ismanaged  = self.IsCellviewInTag(libroot, const.TAG_LATEST, cellname, cellview)
        if(ismanaged == False):
            raise ValueError('{}->{} is not managed'.format(cellname, cellview))

        else:
            # Check if the cell is checkedout by user
            owner = self.GetCellviewLockOwner(libpath_latest, cellname, cellview)
            if(owner is None):
                raise ValueError('{}->{} is not checkedout'.format(cellname, cellview))
            if(owner != user):
                raise ValueError('{}->{} is locked by {}'.format(cellname, cellview, owner,user))

        # Unlock
        hist_file = self.UnlockCellview(libpath_latest, cellname, cellview, user)
        self.svnifc.Unlock(hist_file)
        # Update cell in work tag
        self.UpdateCellview(libroot, cellname, cellview, const.TAG_WORK)

    # Update Lib contents
    def UpdateLibContent(self, libpath, cellname, cellview):
        libroot = CktSyncUtil.FindTypeRoot(const.TYPE_LIB, startdir=libpath)
        tagname = self.GetLibTag(libpath)

        if(cellview != ''):
            # Update cellview
            self.UpdateCellview(libroot, cellname, cellview, tagname)
        elif(cellname != ''):
            # Update cell
            self.UpdateCell(libroot, cellname, tagname)
        else:
            # Update lib
            self.UpdateTag(libroot, tagname)
