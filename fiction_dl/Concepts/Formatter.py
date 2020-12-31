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

from fiction_dl.Concepts.Story import Story
from fiction_dl.Concepts.StoryPackage import StoryPackage

# Standard packages.

from pathlib import Path
from typing import List, Union

#
#
#
# Classes.
#
#
#

##
#
# Represents an abstract formatter - that is, a thing generating an output file from a Story.
#
##

class Formatter:

    def __init__(self, embedImages: bool = True) -> None:

        ##
        #
        # The constructor.
        #
        # @param embedImages Embed images in the output file.
        #
        ##

        self._embedImages = embedImages

    def FormatAndSave(self, story: Union[Story, StoryPackage], filePath: Path) -> bool:

        ##
        #
        # Formats the story (or the story package) and saves it to the output file.
        #
        # @param story    The story/story package to be formatted and saved.
        # @param filePath The path to the output file.
        #
        # @return **True** if the output file was generated and saved without problems, **False**
        #         otherwise.
        #
        ##

        raise NotImplementedError()