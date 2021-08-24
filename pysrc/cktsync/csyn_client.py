#----------------
# This file is part of CktSync design manager
#----------------

import os
from multiprocessing.connection import Client
from .csyn_config import CktSyncConfig

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
      print("No server")
      return 
      
    csynclient.send(cmd)
    resp = csynclient.recv()
    csynclient.close()
    return resp
