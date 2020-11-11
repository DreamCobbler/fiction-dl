####
#
# fiction-dl
# Copyright (C) (2020) Benedykt Synakiewicz <dreamcobbler@outlook.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
####

#
#
#
# Imports.
#
#
#

# Add the fiction_dl package to PATH.

import sys

sys.path.insert(0, "../")

# Application.

from fiction_dl.Core.Application import Application
from fiction_dl.Configuration import *

# Standard packages.

from argparse import Namespace
import logging
from pathlib import Path

# Non-standard packages.

from dreamy_utilities.Filesystem import FindExecutable


#
#
#
# The start-up routine.
#
#
#

# Set up the logger.

logging.basicConfig(level = logging.INFO)

#
# Run the integration test.
#

arguments = Namespace(
    Authenticate = True,
    ClearCache = True,
    Pack = False,
    Verbose = True,
    Force = True,
    Debug = True,
    Images = True,
    PersistentCache = True,
    Username = "",
    Password = "",
    LibreOffice = FindExecutable("soffice", "LibreOffice", "program") or Path(),
    Output = OutputDirectoryPath,
    Input = "Integration Test Dataset 1.txt"
    Audiobook = False,
)

Application(
    arguments = arguments,
    cacheDirectoryPath = CacheDirectoryPath
).Launch()

arguments = Namespace(
    Authenticate = True,
    ClearCache = True,
    Pack = True,
    Verbose = True,
    Force = True,
    Debug = True,
    Images = True,
    PersistentCache = True,
    Username = "",
    Password = "",
    LibreOffice = FindExecutable("soffice", "LibreOffice", "program") or Path(),
    Output = OutputDirectoryPath,
    Input = "Integration Test Dataset 3.txt"
    Audiobook = False,
)

Application(
    arguments = arguments,
    cacheDirectoryPath = CacheDirectoryPath
).Launch()

arguments = Namespace(
    Authenticate = True,
    ClearCache = True,
    Pack = False,
    Verbose = True,
    Force = True,
    Debug = True,
    Images = True,
    PersistentCache = True,
    Username = "",
    Password = "",
    LibreOffice = FindExecutable("soffice", "LibreOffice", "program") or Path(),
    Output = OutputDirectoryPath,
    Audiobook = True,
    Input = "Integration Test Text Sample.txt"
)

Application(
    arguments = arguments,
    cacheDirectoryPath = CacheDirectoryPath
).Launch()