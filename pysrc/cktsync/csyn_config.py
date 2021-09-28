#----------------
# This file is part of CktSync design manager
#----------------

from configparser import ConfigParser
import os
from . import csyn_constants as const

class CktSyncConfig():
    # Initialize
    def __init__(self):
        self.configs = ConfigParser()

    # Read config file
    def Read(self, filename):
        # Check if file exist
        if(os.path.exists(filename) is False):
            raise ValueError('Config file: {} does not exists.'.format(filename))

        # Parse file
        self.configs.read(filename)

    # Write config file
    def Write(self, filename):
        try:
            with open(filename, 'w') as outfile:
                self.configs.write(outfile)
        except:
            raise ValueError('Failed to write config file: {}.'.format(filename))

    # Get value from section and key
    def get(self, section, key):
        return self.configs.get(section, key)

    # Set value in section and key
    def set(self, section, key, value):
        if(section not in self.configs):
            self.configs.add_section(section)
        self.configs.set(section, key, value)

    # Add section
    def add(self, section):
        self.configs.add_section(section)

    # Remove section
    def remove(self, section):
        self.configs.remove_section(section)

    # Get core->type
    def GetCoreType(self):
        dir_type = self.get(const.CONFIG_SECTION_CORE, const.CONFIG_TYPE)
        return dir_type

    # Check if core type is same as argument
    def MatchCoreType(self, coretype):
        dir_type = self.GetCoreType()
        if(dir_type is not None and dir_type == coretype):
            return True
        else:
            return False
