#----------------
# This file is part of CktSync design manager
#----------------

import os
from multiprocessing.connection import Client
from .csyn_config import CktSyncConfig
from . import csyn_osutil as OsUtil
from . import csyn_util as CktSyncUtil
from .csyn_dm import CktSyncDM
from . import csyn_constants as const

# Class for CktSync Client
class CktSyncClient():
    # Initialize
    def __init__(self):
        # Need installation path
        self.csyn_dir = os.environ.get("CKTSYNC_DIR")
        if(self.csyn_dir is None):
            raise ValueError('CKTSYNC_DIR is not defined.')

        # Read config file
        csynconfig = CktSyncConfig()
        cfgpath = os.path.join(self.csyn_dir,"config","cktsync.cfg")
        csynconfig.Read(cfgpath)
        self.server_ip = csynconfig.get("server", "ip")
        self.server_port = csynconfig.get("server", "port")
        if(self.server_ip is None or self.server_port is None):
            raise ValueError('Server or port is not defined in {}.'.format(cfgpath))

        self.server_port = int(self.server_port)

    # Send command to server and get response
    def SendCommand(self, cmd):
        server_address = (self.server_ip, self.server_port)
        # Check if server is running
        try:
            csynclient = Client(server_address)
        except:
            # Send error
            resp_dict = {}
            resp_dict['errcode'] = 1
            resp_dict['msg'] = 'No server running at {}:{}'.format(self.server_ip, self.server_port)
            return resp_dict

        try:
            self.PreprocessCommand(cmd)
        except Exception as e:
            # Send error
            resp_dict = {}
            resp_dict['errcode'] = 1
            resp_dict['msg'] = '{}'.format(e)
            csynclient.close()
            return resp_dict

        csynclient.send(cmd)
        resp_dict = csynclient.recv()
        csynclient.close()

        try:
            self.PostprocessResponse(cmd, resp_dict)
        except Exception as e:
            # Send error
            resp_dict = {}
            resp_dict['errcode'] = 1
            resp_dict['msg'] = '{}'.format(e)
            return resp_dict

        return resp_dict

    # Preprocess for a command
    def PreprocessCommand(self, cmd):
        # Check in
        if(cmd['cmd'] == 'cellci'):
            cellpath = os.path.join(cmd['libpath'], cmd['cellname'])
            cvpath = os.path.join(cellpath, cmd['cellview'])
            # Try to change file permission
            try:
                OsUtil.ChangeFilePermission(cellpath, filemode=0o660)
            except:
                pass

            try:
                os.chmod(cvpath, 0o770)
                OsUtil.ChangeFilePermission(cvpath, filemode=0o660)
            except:
                raise ValueError('Fail to change permission {}->{}'.format(cmd['cellname'], cmd['cellview']))

        # Cancel check out
        elif(cmd['cmd'] == 'cellcanco'):
            cellpath = os.path.join(cmd['libpath'], cmd['cellname'])
            cvpath = os.path.join(cellpath, cmd['cellview'])
            # Try to change file permission
            try:
                OsUtil.ChangeFilePermission(cellpath, filemode=0o660)
            except:
                pass

            try:
                os.chmod(cvpath, 0o770)
                OsUtil.ChangeFilePermission(cvpath, filemode=0o660)
            except:
                raise ValueError('Fail to change permission {}->{}'.format(cmd['cellname'], cmd['cellview']))

    # Post response for a command
    def PostprocessResponse(self, cmd, resp_dict):
        # Error check
        if(resp_dict['errcode'] == 1):
            return

        # Check out
        elif(cmd['cmd'] == 'cellco'):
            cktdm = CktSyncDM('', '', '')
            libpath = cmd['libpath']
            cellname = cmd['cellname']
            cellview = cmd['cellview']
            cellpath = os.path.join(libpath, cellname)
            cvpath = os.path.join(cellpath, cellview)
            libroot = CktSyncUtil.FindTypeRoot(const.TYPE_LIB, startdir=libpath)
            # Copy cellview from latest to work
            try:
                cktdm.CopyCell(libroot, cellname, const.TAG_LATEST, connt.TAG_WORK)
                OsUtil.ChangeFilePermission(cellpath, filemode=0o640)
            except:
                pass

            try:
                cktdm.CopyCellview(libroot, cellname, cellview, const.TAG_LATEST, const.TAG_WORK, copycell=False)
                os.chmod(cvpath, 0o750)
                OsUtil.ChangePermission(cvpath, dirmode=0o750, filemode=0o640)
            except:
                raise ValueError('Fail to copy {}->{} to work'.format(cellname, cellview))
