#----------------
# This file is part of CktSync design manager
#----------------

import os
import argparse
import getpass
from multiprocessing.connection import Listener
from .csyn_config import CktSyncConfig
from .csyn_dm import CktSyncDM

# Class for CktSync Server
class CktSyncServer():
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

        # Verbose
        self.verbose = False

    # Start Server
    def Start(self):
        server_address = (self.server_ip, self.server_port)
        csynserver = Listener(server_address)
        while(True):
            csynclient = csynserver.accept()
            cmd_dict = csynclient.recv()
            try:
                resp_dict = self.ParseCommand(cmd_dict)
            except Exception as e:
                resp_dict = {}
                resp_dict['errcode'] = 1
                resp_dict['msg'] = '{}'.format(e)

            csynclient.send(resp_dict)

            if(self.verbose):
                print('Client : {}'.format(csynclient))
                print('Req : {}'.format(cmd_dict))
                print('Resp : {}'.format(resp_dict))

            csynclient.close()

    # Parse command
    def ParseCommand(self, cmd_dict):
        user = cmd_dict['user']
        resp_dict = {}
        cktdm = CktSyncDM('r', self.username, self.password)
        if(cmd_dict['cmd'] == 'cellci'):
            # Cell checkin
            libpath = cmd_dict['libpath']
            cellname = cmd_dict['cellname']
            cellview = cmd_dict['cellview']
            cimsg = cmd_dict['cimsg']
            cktdm.CiCellview(user, libpath, cellname, cellview, cimsg)
            resp_dict['errcode']=0
            resp_dict['msg'] = 'Checkin successful'

        elif(cmd_dict['cmd'] == 'cellco'):
            # Cell checkout
            libpath = cmd_dict['libpath']
            cellname = cmd_dict['cellname']
            cellview = cmd_dict['cellview']
            cktdm.CoCellview(user, libpath, cellname, cellview)
            resp_dict['errcode']=0
            resp_dict['msg'] = 'Checkout successful'

        return resp_dict

    # Arg parser
    def ArgParser(self, args):
        parser = argparse.ArgumentParser(prog="cktsync server")
        parser.add_argument("password", help="Password for SVN")
        parser.add_argument('--verbose', action='store_true', help='Print output from client')

        parser_result = parser.parse_args(args)

        # Set credential
        self.username = getpass.getuser()
        self.password = parser_result.password

        if(parser_result.verbose):
            self.verbose = True

        # Start server
        self.Start()
