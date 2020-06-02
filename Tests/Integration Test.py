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
from fiction_dl.Utilities.Filesystem import GetLibreOfficeExecutableFilePath
from fiction_dl.Configuration import *

# Standard packages.

from argparse import Namespace
import logging
from pathlib import Path

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
# The first time, with images.
#

arguments = Namespace(
    Authenticate = False,
    ClearCache = True,
    Verbose = True,
    Force = True,
    Debug = True,
    Images = True,
    PersistentCache = True,
    Username = "",
    Password = "",
    LibreOffice = GetLibreOfficeExecutableFilePath() or Path(),
    Output = OutputDirectoryPath / "Images",
    Input = "Integration Test Dataset.txt"
)

Application(
    arguments = arguments,
    cacheDirectoryPath = CacheDirectoryPath
).Launch()

#
# The second time, without images.
#

arguments = Namespace(
    Authenticate = False,
    ClearCache = False,
    Verbose = True,
    Force = True,
    Debug = True,
    Images = False,
    PersistentCache = True,
    Username = "",
    Password = "",
    LibreOffice = GetLibreOfficeExecutableFilePath() or Path(),
    Output = OutputDirectoryPath / "No Images",
    Input = "Integration Test Dataset.txt"
)

Application(
    arguments = arguments,
    cacheDirectoryPath = CacheDirectoryPath
).Launch()