#----------------
# This file is part of CktSync design manager
#----------------

from configparser import ConfigParser
import os

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
