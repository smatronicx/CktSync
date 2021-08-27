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
    # Create config file
    self.config = CktSyncConfig()
    
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
    self.config.set('core','type','project')
    self.WriteConfig()
  
  # Read current config file
  def ReadConfig(self):
    # Check if .csync/config file exists
    projdir = os.getcwd()
    csync_dir = os.path.join(projdir, '.csync')
    config_file = os.path.join(csync_dir, 'config')
    if(os.path.exists(config_file) == False):
      raise ValueError('{} is not managed by CktSync.'.format(projdir))
    
    
    # Read config file
    self.config.Read(config_file)
  
  # Write current config file
  def WriteConfig(self):
    # Write to .csync/config file exists
    projdir = os.getcwd()
    csync_dir = os.path.join(projdir, '.csync')
    config_file = os.path.join(csync_dir, 'config')
    self.config.Write(config_file)
    
  # Find project root dir
  def FindProjectRoot(self):
    startdir = os.getcwd()
    while(True):
      projdir = os.getcwd()
      csync_dir = os.path.join(projdir, '.csync')
      config_file = os.path.join(csync_dir, 'config')
      config = CktSyncConfig()
      try:
        # Check if current dir is project root
        config.Read(config_file)
        dir_type = config.get('core', 'type')
	
	
	# Found project path, return
        if(dir_type is not None and dir_type == 'project'):
          return
      except:
        pass
      
      # Move to upper folder
      try:
        os.chdir(os.path.pardir)
	# Check for root
        if(projdir == os.getcwd()):
          break
      except:
        break
	
    # Not in project folder
    raise ValueError('{} is not under any project.'.format(startdir))
  
  # Configure project
  def ConfigProject(self, args):
    self.FindProjectRoot()
    self.ReadConfig()
    # Update config
    if('repo' in args):
      self.config.set('svn', 'repo', args.repo)
    
    self.WriteConfig()
    
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
    
    # Populate
    elif(parser_result.subcmd == 'populate'):
      self.PopulateProject()
    
    # Print help
    else:
      parser.print_help()
