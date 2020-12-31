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

# Application.

from fiction_dl.Extractors.ExtractorXenForo import ExtractorXenForo

# Standard packages.

from typing import List

#
#
#
# Classes.
#
#
#

##
#
# Extractor designed for SpaceBattles.com. Internally it uses the XenForo extractor.
#
##

class ExtractorSpaceBattles(ExtractorXenForo):

    def __init__(self) -> None:

        ##
        #
        # The constructor.
        #
        ##

        super().__init__("https://forums.spacebattles.com/")

    def GetSupportedHostnames(self) -> List[str]:

        ##
        #
        # Returns a list of hostnames supposed to be supported by the extractor.
        #
        # @return A list of supported hostnames.
        #
        ##

        return [
            "spacebattles.com"
        ]