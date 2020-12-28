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

# Application.

from fiction_dl.Concepts.Chapter import Chapter
from fiction_dl.Concepts.Extractor import Extractor

# Standard packages.

from datetime import datetime
import logging
import re
from typing import List, Optional

# Non-standard packages.

from bs4 import BeautifulSoup
from dreamy_utilities.HTML import ReadElementText
from dreamy_utilities.Text import FindFirstMatch, Stringify
from dreamy_utilities.Web import GetHostname

#
#
#
# Classes.
#
#
#

##
#
# An extractor dedicated for Ralst.com.
#
##

class ExtractorRalst(Extractor):

    def __init__(self) -> None:

        ##
        #
        # The constructor.
        #
        ##

        super().__init__()

        self._chapterParserName = "html5lib"

    def GetSupportedHostnames(self) -> List[str]:

        ##
        #
        # Returns a list of hostnames supposed to be supported by the extractor.
        #
        # @return A list of supported hostnames.
        #
        ##

        return [
            "ralst.com",
        ]

    def _InternallyScanStory(
        self,
        URL: str,
        soup: Optional[BeautifulSoup]
    ) -> bool:

        ##
        #
        # Scans the story: generates the list of chapter URLs and retrieves the
        # metadata.
        #
        # @param URL  The URL of the story.
        # @param soup The tag soup.
        #
        # @return **False** when the scan fails, **True** when it doesn't fail.
        #
        ##

        # Retrieve the metadata.

        metadataElement = soup.select("p")[1]

        metadataText = metadataElement.get_text().strip()
        metadataText.replace(r"\n", " ")
        metadataText = metadataText.split("\n")
        if len(metadataText) < 2:
            logging.error("Invalid metadata text format.")
            return False

        title = metadataText[0]
        author = metadataText[1][3:]

        # Set the metadata.

        self.Story.Metadata.Title = title
        self.Story.Metadata.Author = author

        self.Story.Metadata.DatePublished = "?"
        self.Story.Metadata.DateUpdated = "?"

        self.Story.Metadata.ChapterCount = 1
        self.Story.Metadata.WordCount = 0

        self.Story.Metadata.Summary = "No summary."

        # Set chapter URLs.

        self._chapterURLs = [URL]

        # Return.

        return True

    def _InternallyExtractChapter(
        self,
        URL: str,
        soup: Optional[BeautifulSoup]
    ) -> Optional[Chapter]:

        ##
        #
        # Extracts specific chapter.
        #
        # @param URL  The URL of the page containing the chapter.
        # @param soup The tag soup of the page containing the chapter.
        #
        # @return **True** if the chapter is extracted correctly, **False** otherwise.
        #
        ##

        contentElements = soup.select("p")

        contentElements[0].decompose()
        contentElements[1].decompose()

        contentElements[-1].decompose()
        contentElements[-2].decompose()
        contentElements[-3].decompose()

        return Chapter(
            title = None,
            content = Stringify(soup)
        )