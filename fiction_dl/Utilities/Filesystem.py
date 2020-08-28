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
from string import ascii_letters, digits
import sys
from typing import Optional, Union
from uuid import uuid4

#
#
#
# Functions.
#
#
#

def AddToPATH(path: Path) -> None:

    ##
    #
    # Adds a directory path to the PATH variable.
    #
    # @param path The directory path to be added.
    #
    ##

    if not path.is_dir():
        return

    sys.path.insert(0, str(path))

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

def GetUniqueFileName() -> str:

    ##
    #
    # Returns a unique file name. Useful for creating temporary files.
    #
    # @return A unique file name.
    #
    ##

    return uuid4().hex

def ReadTextFile(filePath: Union[Path, str]) -> Optional[str]:

    ##
    #
    # Opens and reads a text file, returning its contents as a string.
    #
    # @param filePath Path to the text file.
    #
    # @return The contents of the file. Optionally None, if the function has failed to read the
    #         file.
    #
    ##

    if not filePath:
        return None

    try:

        with open(filePath, "r", encoding = "utf-8") as file:
            return file.read()

    except OSError:

        return None

def SanitizeFileName(string: str) -> str:

    ##
    #
    # Creates a valid file name from any string.
    #
    # @param string The input string to be sanitized.
    #
    ##

    ValidCharacters = f"-',_.()[] {ascii_letters}{digits}"

    return "".join(x for x in string if x in ValidCharacters)

def WriteTextFile(filePath: Path, content: str) -> bool:

    ##
    #
    # Writes the content to a text file. The file is created/overwrriten. The directory in which the
    # file resides/will reside will be created if necessary.
    #
    # @param filePath File path.
    # @param content File content.
    #
    # @return **True** if the file was written successfully, **False** otherwise.
    #
    ##

    if not filePath:
        return False

    filePath.parent.mkdir(parents = True, exist_ok = True)

    try:

        with open(filePath, "w", encoding = "utf-8") as file:
            file.write(content)

        return True

    except OSError:

        return False