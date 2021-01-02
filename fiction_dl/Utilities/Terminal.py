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

from typing import List, Optional

#
#
#
# Functions.
#
#
#

def ReadString(
    description: str,
    options: Optional[List[str]] = None,
    default: Optional[str] = None
) -> str:

    ##
    #
    # Reads a string value from the uer.
    #
    # @param description The question asked.
    # @param default     The default value.
    #
    # @return Read value.
    #
    ##

    if options:

        optionsDescription = "/".join(options)
        readValue = input(f"{description} ({optionsDescription}) [{default}]: ")

        return readValue if (readValue in options) else default

    else:

        readValue = input(f"{description}: ")

        return readValue