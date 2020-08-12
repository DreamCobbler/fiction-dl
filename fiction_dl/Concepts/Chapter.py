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

import re
from typing import Optional

# Non-standard packages.

from titlecase import titlecase

#
#
#
# Classes.
#
#
#

##
#
# Represents a single chapter of a story.
#
##

class Chapter:

    def __init__(self, title: Optional[str] = None, content: Optional[str] = None) -> None:

        ##
        #
        # The constructor.
        #
        # @param title   The title of the chapter.
        # @param content The content of the chapter.
        #
        ##

        self.Title = title
        self.Content = content

    def Process(self) -> None:

        ##
        #
        # Processes the chapter. To be used before generating output file.
        #
        ##

        if self.Title:

            self.Title = re.sub(
                "\[?\(?Chapter \d+\:?\)?\]?\s*\.?-?\s*",
                "",
                self.Title,
                flags = re.IGNORECASE
            )

            self.Title = titlecase(self.Title)

            if not self.Title:
                self.Title = None

    def __bool__(self) -> bool:

        ##
        #
        # The bool operator.
        #
        # @return **True** if the chapter has any content.
        #
        ##

        return bool(self.Content)