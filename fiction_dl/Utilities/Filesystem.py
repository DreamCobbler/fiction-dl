####
#
# fiction-dl
# Copyright (C) (2020 - 2021) Benedykt Synakiewicz <dreamcobbler@outlook.com>
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

from pathlib import Path
from typing import Optional

# Non-standard packages.

from dreamy_utilities.Filesystem import FindExecutable

#
#
#
# Functions.
#
#
#

def GetLibreOfficeExecutablePath() -> Optional[Path]:

    ##
    #
    # Returns the path to the LibreOffice executable (soffice[.exe]).
    #
    # @return The path to the executable.
    #
    ##

    if (path := FindExecutable("soffice", "LibreOffice", "program")):
        return path

    try:

        import winreg

        registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        if not registry:
            return None

        for majorVersion in range(5, 7 + 1):

            for minorVersion in range(0, 9 + 1):

                version = f"{majorVersion}.{minorVersion}"

                try:

                    key = winreg.OpenKey(
                        registry,
                        f"SOFTWARE\\The Document Foundation\\LibreOffice\\{version}\\Capabilities"
                    )

                    value, _ = winreg.QueryValueEx(key, "ApplicationIcon")
                    if not value.endswith(".bin,0"):
                        return None

                    value = value[:-6] + ".exe"

                    path = Path(value)
                    if path.is_file():
                        return path
                    else:
                        return None

                except FileNotFoundError:

                    continue

    except ImportError:

        return None

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