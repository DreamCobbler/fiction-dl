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

from fiction_dl.Concepts.Metadata import Metadata
from fiction_dl.Concepts.Story import Story
import fiction_dl.Configuration as Configuration

# Standard packages.

from typing import Callable, List

# Non-standard packages.

from dreamy_utilities.Containers import RemoveDuplicates
from dreamy_utilities.Text import FillTemplate, GetCurrentDate, PrettifyNumber

#
#
#
# Classes.
#
#
#

##
#
# Represents a group (list) of stories.
#
##

class StoryPackage:

    def __init__(
        self,
        stories: List[Story]
    ) -> None:

        ##
        #
        # The constructor.
        #
        # @param stories Stories included in the package.
        #
        ##

        # Initialize member variables.

        self.Metadata = Metadata(prettifyTitle = False)

        self.Stories = stories
        self.Images = []

        # Generate/calculate some metadata. Also extract images.

        totalAuthors = []
        totalChapterCount = 0
        totalWordCount = 0

        for story in self.Stories:

            totalAuthors.append(story.Metadata.Author)
            totalChapterCount += story.Metadata.ChapterCount
            totalWordCount += story.Metadata.WordCount

            self.Images.extend(story.Images)

        totalAuthors = RemoveDuplicates(totalAuthors)

        # Initialize the metadata.

        self.Metadata.URL = "n/a"

        self.Metadata.Title = f"{Configuration.ApplicationName} Package ({GetCurrentDate()})"
        self.Metadata.Author = ", ".join(totalAuthors)
        self.Metadata.Summary = "n/a"

        self.Metadata.DatePublished = stories[0].Metadata.DateExtracted
        self.Metadata.DateUpdated = stories[0].Metadata.DateExtracted
        self.Metadata.DateExtracted = stories[0].Metadata.DateExtracted

        self.Metadata.ChapterCount = totalChapterCount
        self.Metadata.WordCount = totalWordCount

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
        template = template.replace("@@@StoryCount@@@", PrettifyNumber(len(self.Stories)))

        return template

    def Join(
        self,
        prefixer: Callable[[int, str, str], str] = None,
        processor: Callable[[str], str] = None
    ) -> str:

        ##
        #
        # Returns the whole content of all the stories, with each chapter prefixed with the given
        # prefix and its content processed using given the given processor.
        #
        # @param prefixer  A function accepting (index, chapter title, story title) and returning a string. Optional.
        # @param processor A function used to process the content of each chapter. Takes a
        #                  string and returns a string.
        #
        # @return Processed story content.
        #
        ##

        joinedContent = ""

        for story in self.Stories:

            prettifiedTitle = story.Metadata.GetPrettified().Title

            for index, chapter in enumerate(story.Chapters, start = 1):

                prefix = prefixer(index, chapter.Title, prettifiedTitle) if prefixer else ""
                content = processor(chapter.Content) if processor else chapter.Content

                joinedContent += (prefix  + content)

        return joinedContent