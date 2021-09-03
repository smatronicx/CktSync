#----------------
# This file is part of CktSync design manager
#----------------

import os
from .csyn_svn import CktSyncSvn
from .csyn_config import CktSyncConfig
from . import csyn_util as CktSyncUtil
import glob


# Class for CktSync design management interface
class CktSyncDM():
  # Initialize
  def __init__(self, repo, user, passwd):
    self.svnifc = CktSyncSvn(repo, user, passwd)

  # Fix permission
  def FixPermission(self):
    pass
  
  # Check if the lib path is managed by cktsync
  def ManagedLib(self, libpath):
    csync_dir = os.path.join(libpath, '.csync')
    config_file = os.path.join(csync_dir, 'config')
    config = CktSyncConfig()
    try:
      # Check if it is lib dir 
      config.Read(config_file)
      dir_type = config.get('core', 'type')
      if(dir_type is not None and dir_type == 'library'):
        return True
      else:
        return False
    except:
      return False
  
  # Get lib tag
  def GetLibTag(self, libpath):
    csync_dir = os.path.join(libpath, '.csync')
    config_file = os.path.join(csync_dir, 'config')
    config = CktSyncConfig()
    try:
      # Check if it is lib tag dir 
      config.Read(config_file)
      dir_type = config.get('core', 'type')
      if(dir_type is None or dir_type != 'tag'):
        return None
    except:
      return None
    
    tag_type = config.get('tag', 'type')
         
    return tag_type
  
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
      config.Read(csync_lock)
      lock_owner = config.set('lock', 'user', user)
      config.Write(csync_lock)
    except:
      raise ValueError('Failed to lock {}->{}'.format(cellname, cellview))
    
    self.svnifc.Lock(csync_lock)
  
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
      cvpath = os.path.join(libpath, cellname, cellview, '*')
      self.svnifc.Add(cvpath)
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
      CktSyncUtil.ChangePermission(cvpath, 0o750, 0o440)
    
    else:
      raise ValueError('Checkin failed for {}->{}'.format(cellname, cellview))
  
  # Checkout cellview
  def CoCellview(self, user, libpath, cellname, cellview):
    # Check if libpath is in worktag
    libtag = self.GetLibTag(libpath)
    if(libtag is None or libtag != 'work'):
      raise ValueError('Library {} is not in worktag'.format(libpath))
     
    # Create cell
    self.CreateCell(libpath, cellname)
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
	  
