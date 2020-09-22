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

# Standard packages.

from os.path import expandvars, isfile
from pathlib import Path
from shutil import which
from typing import Optional

#
#
#
# Functions.
#
#
#

def FindEbookConvert() -> bool:

    if not which("ebook-convert"):
        return False

    return True

def GetLibreOfficeExecutableFilePath() -> Optional[Path]:

    ##
    #
    # Returns file path leading to the LibreOffice/OpenOffice executable.
    #
    # @return The file path to the LibreOffice executable.
    #
    ##

    path = which("soffice")
    if path:
        return Path(path)

    path = expandvars("%ProgramW6432%\LibreOffice\program\soffice.exe")
    if isfile(path):
        return Path(path)

    path = expandvars("%ProgramFiles(x86)%\LibreOffice\program\soffice.exe")
    if isfile(path):
        return Path(path)

    path = "/usr/bin/soffice"
    if isfile(path):
        return Path(path)

    path = "/bin/soffice"
    if isfile(path):
        return Path(path)

    return None

def GetPackageDirectory() -> Path:

    ##
    #
    # Returns a path to the main directory of the package. Useful for packed files.
    #
    # @return The path to the package directory.
    #
    ##

    return Path(__file__).parent.parent.absolute()