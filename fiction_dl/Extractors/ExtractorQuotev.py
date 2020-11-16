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
from fiction_dl.Concepts.Story import Story
from fiction_dl.Utilities.HTML import StripHTML

# Standard packages.

import logging
import re
import requests
from typing import List, Optional

# Non-standard packages.

from bs4 import BeautifulSoup
from dreamy_utilities.Text import Stringify
from dreamy_utilities.Web import DownloadSoup, GetHostname

#
#
#
# Classes.
#
#
#

##
#
# An extractor dedicated for Quotev.com.
#
##

class ExtractorQuotev(Extractor):

    def __init__(self) -> None:

        ##
        #
        # The constructor.
        #
        ##

        super().__init__()

    def GetSupportedHostnames(self) -> List[str]:

        ##
        #
        # Returns a list of hostnames supposed to be supported by the extractor.
        #
        # @return A list of supported hostnames.
        #
        ##

        return [
            "quotev.com",
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

        # Locate relevant page elements.

        titleElement = soup.select_one("div#quizHeaderTitle > h1")
        if not titleElement:
            logging.error("Title element not found.")
            return False

        authorElement = soup.select_one("div#quizHeaderTitle > div.quizAuthorList")
        if not authorElement:
            logging.error("Author element not found.")
            return False

        summaryElement = soup.select("div#quizHeaderTitle > div")[-1]
        if not summaryElement:
            logging.error("Summary element not found.")
            return False

        # Extract the metadata.

        metadataElement = soup.select_one("div#quizHeaderInner")
        if not metadataElement:
            logging.error("Metadata element not found.")
            return False

        timeElements = metadataElement.select("time.q_time")
        if not len(timeElements):
            logging.error("Date published/updated not found.")
            return False

        datePublishedElement = timeElements[0]
        dateUpdatedElement = timeElements[1] if len(timeElements) > 1 else datePublishedElement

        # Extract chapter URLs.

        if (chaptersElement := soup.select_one("div#rselectList")):

            for element in chaptersElement.select("a"):

                if not element.has_attr("href"):
                    continue

                self._chapterURLs.append(element["href"])

        else:

            self._chapterURLs = [URL]

        if not self._chapterURLs:
            logging.error("Chapters not found.")
            return False

        # Set the metadata.

        self.Story.Metadata.Title = titleElement.get_text().strip()
        self.Story.Metadata.Author = authorElement.get_text().strip()

        self.Story.Metadata.DatePublished = datePublishedElement["datetime"][:10]
        self.Story.Metadata.DateUpdated = dateUpdatedElement["datetime"][:10]

        self.Story.Metadata.ChapterCount = len(self._chapterURLs)
        self.Story.Metadata.WordCount = 0

        self.Story.Metadata.Summary = StripHTML(summaryElement.get_text().strip())

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

        # Locate relevant page elements.

        titleElement = soup.select_one("h2#quizSubtitle")
        if not titleElement:
            logging.error("Title element not found.")
            return False

        contentElement = soup.select_one("#rescontent")
        if not contentElement:
            logging.error("Content element not found.")
            return False

        # Return.

        return Chapter(
            titleElement.get_text().strip(),
            Stringify(contentElement.encode_contents())
        )