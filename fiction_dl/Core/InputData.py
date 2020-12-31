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

from fiction_dl.Utilities.Extractors import CreateExtractor
import fiction_dl.Configuration as Configuration

# Standard packages.

import random
from typing import List

# Non-standard packages.

from dreamy_utilities.Containers import RemoveDuplicates

#
#
#
# Classes.
#
#
#

##
#
# Represents the input arguments (URLs or file paths).
#
##

class InputData:

    def __init__(self, initialArgument: str) -> None:

        ##
        #
        # The constructor.
        #
        # @param initialArgument The original argument provided by the user.
        #
        ##

        self._expandedArguments = [initialArgument]

    def Access(self) -> List[str]:

        ##
        #
        # Returns the list of story URLs found in the input data.
        #
        # @return A list of story URLs.
        #
        ##

        return self._expandedArguments

    def Expand(self) -> int:

        ##
        #
        # Expands every input argument that can be expanded.
        #
        # @return The number of arguments that have been expanded.
        #
        ##

        if not self._expandedArguments:
            return 0

        newExpandedData = []
        expandedArgumentsCount = 0

        for argument in self._expandedArguments:

            extractor = CreateExtractor(argument)
            if not extractor:
                newExpandedData.append(argument)
                continue

            if not (retrievedStoryURLs := extractor.ScanChannel(argument)):

                newExpandedData.append(argument)

            else:

                newExpandedData.extend(retrievedStoryURLs)
                expandedArgumentsCount += 1

        newExpandedData = RemoveDuplicates(newExpandedData)

        self._expandedArguments = newExpandedData
        return expandedArgumentsCount

    def ExpandAndShuffle(self) -> None:

        ##
        #
        # Expands every input argument that can be expanded, recursively, then randomly reorders
        # the list.
        #
        ##

        expandedArgumentsCount = 1

        while 0 != expandedArgumentsCount:
            expandedArgumentsCount = self.Expand()

        random.shuffle(self._expandedArguments)