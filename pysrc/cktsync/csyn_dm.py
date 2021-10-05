#----------------
# This file is part of CktSync design manager
#----------------

import os
from .csyn_svn import CktSyncSvn
from .csyn_config import CktSyncConfig
from .csyn_dmbase import CktSyncDMBase
from . import csyn_util as CktSyncUtil
from . import csyn_osutil as OsUtil
from . import csyn_constants as const


# Class for CktSync design management interface
class CktSyncDM(CktSyncDMBase):
    # Initialize
    def __init__(self, repo, user, passwd):
        super().__init__(repo, user, passwd)

    
