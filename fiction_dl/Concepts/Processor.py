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

from typing import Optional

#
#
#
# Classes.
#
#
#

##
#
# Represents an abstract processor, i.e. a tool processing the content of the story in some way.
#
##

class Processor:

    def Process(self, content: str) -> Optional[str]:

        ##
        #
        # Processes the content given and returns a modified version of it.
        #
        # @param content The content to be processed.
        #
        # @return The processed content.
        #
        ##

        raise NotImplementedError()