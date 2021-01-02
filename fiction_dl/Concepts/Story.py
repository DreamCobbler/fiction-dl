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

from fiction_dl.Concepts.Image import Image
from fiction_dl.Concepts.Metadata import Metadata
from fiction_dl.Utilities.HTML import StripHTML
import fiction_dl.Configuration as Configuration

# Standard packages.

from typing import Callable

# Non-standard packages.

from dreamy_utilities.Text import FillTemplate, GetCurrentDate

#
#
#
# Classes.
#
#
#

##
#
# Represents a story.
#
##

class Story:

    def __init__(self, URL: str = "") -> None:

        ##
        #
        # The constructor.
        #
        # @param URL The URL leading to the story.
        #
        ##

        self.Metadata = Metadata()

        self.Metadata.URL = URL
        self.Metadata.DatePublished = GetCurrentDate()
        self.Metadata.DateUpdated = self.Metadata.DatePublished
        self.Metadata.DateExtracted = self.Metadata.DatePublished

        self.Chapters = []
        self.Images = []

    def FillTemplate(self, template: str, escapeHTMLEntities: bool = False) -> str:

        ##
        #
        # Replaces placeholders with appropriate values.
        #
        # @param template The code of the template to be filled.
        #
        # @return Filled template.
        #
        ##

        template = FillTemplate(Configuration, template)
        template = FillTemplate(self.Metadata.GetPrettified(escapeHTMLEntities), template)

        return template

    def CalculateWordCount(self) -> int:

        ##
        #
        # Calculates the total word count of the story. **Calculates** it, not just returns the
        # .WordCount variable. Might take a moment for longer stories.
        #
        # @return The word count.
        #
        ##

        if not self.Chapters:
            return 0

        wordCount = 0

        for chapter in self.Chapters:
            wordCount += len(StripHTML(chapter.Content).split())

        return wordCount

    def Join(
        self,
        prefixer: Callable[[int, str, str], str] = None,
        processor: Callable[[str], str] = None
    ) -> str:

        ##
        #
        # Returns the whole content of the story, with each chapter prefixed with the given prefix
        # and its content processed using given the given processor.
        #
        # @param prefixer  A function accepting (index, chapter title, story title) and returning a string. Optional.
        # @param processor A function used to process the content of each chapter. Takes a
        #                  string and returns a string.
        #
        # @return Processed story content.
        #
        ##

        joinedContent = ""
        prettifiedTitle = self.Metadata.GetPrettified().Title

        for index, chapter in enumerate(self.Chapters, start = 1):

            prefix = prefixer(index, chapter.Title, prettifiedTitle) if prefixer else ""
            content = processor(chapter.Content) if processor else chapter.Content

            joinedContent += (prefix  + content)

        return joinedContent

    def Process(self) -> None:

        ##
        #
        # Processes the story metadata. To be used before generating output files.
        #
        ##

        self.Metadata.Process()

        for chapter in self.Chapters:
            chapter.Process()

    def __bool__(self) -> bool:

        ##
        #
        # The bool operator.
        #
        # @return **True** if the story has any content.
        #
        ##

        return bool(self.Metadata) and bool(self.Chapters)