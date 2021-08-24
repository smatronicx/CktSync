#----------------
# This file is part of CktSync design manager
#----------------

import os
import argparse
from .csyn_config import CktSyncConfig

# Class for CktSync Project manager
class CktSyncProject():
  # Initialize
  def __init__(self):
    pass
    
  # Init Project
  def InitProject(self):
    # Create config file and place it in .csync folder
    # Check if .csync folder exists
    projdir = os.getcwd()
    csync_dir = os.path.join(projdir, '.csync')
    config_file = os.path.join(csync_dir, 'config')
    
    if(os.path.exists(csync_dir) == True):
      raise ValueError('{} is managed by CktSync.'.format(projdir))
    
    
    try:
      os.mkdir(csync_dir, mode=0o750)
    except:
      print('Unable to initialize project in {}'.format(projdir))
    
    # Create config file
    config = CktSyncConfig()
    config.set('core','type','project')
    config.Write(config_file)
  
  # Read current config file
  def ReadConfig(self):
    # Check if .csync/config file exists
    projdir = os.getcwd()
    csync_dir = os.path.join(projdir, '.csync')
    config_file = os.path.join(csync_dir, 'config')
    if(os.path.exists(config_file) == False):
      raise ValueError('{} is not managed by CktSync.'.format(projdir))
    
    
    # Read config file
    self.config = CktSyncConfig()
    self.config.Read(config_file)
    
  # Configure project
  def ConfigProject(self, args):
    self.ReadConfig()
    
  # Arg parser
  def ArgParser(self, args):
    parser = argparse.ArgumentParser(prog="cktsync project")
    
    subparsers = parser.add_subparsers(dest='subcmd')
    parser_init = subparsers.add_parser('init', 
      help='Initialize project in a folder')
    
    parser_config = subparsers.add_parser('config', 
      help='Configure project')
    parser_config.add_argument('--repo', help='Path to svn repo')
    
    parser_result = parser.parse_args(args)
    # Init
    if(parser_result.subcmd == 'init'):
      self.InitProject()
      
    #Configure
    elif(parser_result.subcmd == 'config'):
      if(len(args) < 2):
        parser_config.print_help()
      else:
        self.ConfigProject(parser_result)
    
    # Print help
    else:
      parser.print_help()
