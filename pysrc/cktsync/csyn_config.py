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
    def Write(self, filename, force=False, makero=False):
        if(force == True):
            # Try to change the mode to 644
            try:
                os.chmod(filename, 0o644)
            except:
                pass
        # Write file
        try:
            with open(filename, 'w') as outfile:
                self.configs.write(outfile)
        except:
            raise ValueError('Failed to write config file: {}.'.format(filename))

        # Make it readonly
        if(makero == True):
            # Try to change the mode to 444
            try:
                os.chmod(filename, 0o444)
            except:
                pass

    # Get value from section and key
    def get(self, section, key):
        return self.configs.get(section, key)

    # Set value in section and key
    def set(self, section, key, value):
        if(section not in self.configs):
            self.configs.add_section(section)
        self.configs.set(section, key, value)

    # Unset a key in section
    def unset(self, section, key):
        if(section not in self.configs):
            pass
        self.configs.remove_option(section, key)

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

    # Set core->type
    def SetCoreType(self, type):
        self.set(const.CONFIG_SECTION_CORE, const.CONFIG_TYPE, type)

    # Check if core type is same as argument
    def MatchCoreType(self, coretype):
        dir_type = self.GetCoreType()
        if(dir_type is not None and dir_type == coretype):
            return True
        else:
            return False
