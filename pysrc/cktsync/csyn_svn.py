#----------------
# This file is part of CktSync design manager
#----------------

import os
import subprocess

# Class for CktSync<->svn interface
class CktSyncSvn():
  # Initialize
  def __init__(self, repo, user, passwd):
    self.repo = repo
    self.svn_base = [
      'svn',
      '--username', user,
      '--password', passwd,
      '--non-interactive',
      '--no-auth-cache'
    ]
  
  # Execute svn command
  def CommandExec(self, cmd):
    cmdout = subprocess.run(cmd, capture_output=True)
    if(cmdout.returncode != 0):
      raise ValueError(cmdout.stderr)
      
    return cmdout
  
  # Add item to svn
  def Add(self, item):
    cmd = self.svn_base.copy()
    cmd.extend(['add', '--parent', item])
    cmdout = self.CommandExec(cmd)
    return cmdout
  
  # Remove item from svn
  def Remove(self, item):
    cmd = self.svn_base.copy()
    cmd.extend(['rm', item])
    cmdout = self.CommandExec(cmd)
    return cmdout
  
  # Commit to repo
  def Commit(self, msg):
    cmd = self.svn_base.copy()
    cmd.extend(['commit', '-m', msg])
    cmdout = self.CommandExec(cmd)
    return cmdout
 
  # Lock file
  def Lock(self, item):
    cmd = self.svn_base.copy()
    cmd.extend(['lock', item])
    cmdout = self.CommandExec(cmd)
    return cmdout
  
  # Unlock file
  def Unlock(self, item):
    cmd = self.svn_base.copy()
    cmd.extend(['unlock', item])
    cmdout = self.CommandExec(cmd)
    return cmdout
  
  # Info
  def Info(self, item):
    cmd = self.svn_base.copy()
    cmd.extend(['info', item])
    cmdout = self.CommandExec(cmd)
    return cmdout
