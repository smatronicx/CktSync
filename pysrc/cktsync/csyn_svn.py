#----------------
# This file is part of CktSync design manager
#----------------

import os
import subprocess
from . import csyn_util as CktSyncUtil
from . import csyn_osutil as OsUtil
from . import csyn_constants as const

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
        cmd.extend(['add', '--parents', '--force', item])
        cmdout = self.CommandExec(cmd)
        return cmdout

    # Add all the children
    def AddAll(self, item, ignorelist=[]):
        cmd = self.svn_base.copy()
        cmd.extend(['add', '--parents', '--force', '--depth=infinity', item])
        cmdout = self.CommandExec(cmd)
        return cmdout


    # Add single item
    def AddSingle(self, item):
        cmd = self.svn_base.copy()
        cmd.extend(['add', '--parents', '--force', '--depth=empty', item])
        cmdout = self.CommandExec(cmd)
        return cmdout

    # Remove item from svn
    def Remove(self, item):
        cmd = self.svn_base.copy()
        cmd.extend(['rm', '--force', item])
        cmdout = self.CommandExec(cmd)
        return cmdout

    # Commit to repo
    def Commit(self, msg):
        cmd = self.svn_base.copy()
        cmd.extend(['commit', '-m', msg])
        cmdout = self.CommandExec(cmd)
        return cmdout

    # Commit single item to repo
    def CommitSingle(self, msg, item):
        cmd = self.svn_base.copy()
        cmd.extend(['commit', '-m', msg, '--depth=empty', item])
        cmdout = self.CommandExec(cmd)
        return cmdout

    # Commit items to repo
    def CommitItem(self, msg, items):
        cmd = self.svn_base.copy()
        cmd.extend(['commit', '-m', msg])
        cmd.extend(items)
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

    # Check for lock owner
    def LockOwner(self, item):
        if(self.IsManaged(item) == False):
            return None
        lock_info = self.InfoDict(item)
        return lock_info.get(const.SVN_LOCKOWNER)

    # Info
    def Info(self, item):
        cmd = self.svn_base.copy()
        cmd.extend(['info', item])
        cmdout = self.CommandExec(cmd)
        return cmdout

    # Checkout
    def Checkout(self, item):
        cmd = self.svn_base.copy()
        cmd.extend(['checkout', item, '.'])
        cmdout = self.CommandExec(cmd)
        return cmdout

    # Update
    def Update(self, item):
        cmd = self.svn_base.copy()
        cmd.extend(['update', item])
        cmdout = self.CommandExec(cmd)
        return cmdout

    # Info to dictionary
    def InfoDict(self, item):
        cmdout = self.Info(item)
        # Get the lines for dictionary
        dictlines = cmdout.stdout.decode('utf-8').split('\n')
        rtndict = {}
        for dictline in dictlines:
            # Find lines with key-value
            if(dictline.find(':') != -1):
                kvtokens = dictline.split(':')
                key = kvtokens[0].strip()
                value = ':'.join(kvtokens[1:]).strip()
                rtndict[key] = value

        # Return the key-values
        return rtndict

    # Check if item is under svn
    def IsManaged(self, item):
        try:
            info = self.Info(item)
            return True
        except Exception as e:
            err = repr(e)
            if(const.SVN_WORKINGCOPY in err):
                return False
            raise ValueError(e)
