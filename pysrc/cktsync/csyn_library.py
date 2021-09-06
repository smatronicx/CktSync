#----------------
# This file is part of CktSync design manager
#----------------

import os
import argparse
from .csyn_config import CktSyncConfig
from . import csyn_util as CktSyncUtil
from .csyn_client import CktSyncClient

# Class for CktSync Library manager
class CktSyncLibrary():
    # Initialize
    def __init__(self):
        # Create config file
        self.config = CktSyncConfig()

    # Create Library
    def CreateLibrary(self, ):
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

    # Configure project
    def ConfigProject(self, args):
        startdir = os.getcwd()
        try:
            CktSyncUtil.FindTypeRoot('project')
        except:
            raise ValueError('{} is not under any project.'.format(startdir))

        self.ReadConfig()
        # Update config
        if('repo' in args):
            self.config.set('svn', 'repo', args.repo)

        self.WriteConfig()

    # Populate project
    def PopulateProject(self):
        # Move to pject root
        startdir = os.getcwd()
        try:
            CktSyncUtil.FindTypeRoot('project')
        except:
            raise ValueError('{} is not under any project.'.format(startdir))

        self.ReadConfig()
        repo = self.config.get('svn', 'repo')
        if(repo is None):
            raise ValueError('repo is not set for project.')

        projrepo = CktSyncSvn(repo, '', '')
        projrepo.Checkout(repo)
        projrepo.Update()

    # Arg parser
    def ArgParser(self, args):
        parser = argparse.ArgumentParser(prog="cktsync project")

        subparsers = parser.add_subparsers(dest='subcmd')
        parser_init = subparsers.add_parser('init',
            help='Initialize project in a folder')

        parser_config = subparsers.add_parser('config',
            help='Configure project')
        parser_config.add_argument('--repo', help='Path to svn repo')

        parser_populate = subparsers.add_parser('populate',
            help='Populate project folder')

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
