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
# An extractor dedicated for FicWad.com.
#
##

class ExtractorFicWad(Extractor):

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
            "ficwad.com",
        ]

    def ScanChannel(self, URL: str) -> Optional[List[str]]:

        ##
        #
        # Scans the channel: generates the list of story URLs.
        #
        # @return **None** when the scan fails, a list of story URLs when it doesn't fail.
        #
        ##

        if (not URL) or (GetHostname(URL) not in self.GetSupportedHostnames()):
            return None

        if "/a/" not in URL:
            return None

        soup = self._webSession.GetSoup(URL)
        if not soup:
            logging.error(f"Couldn't download page: \"{URL}\".")
            return None

        storyURLs = []

        for element in soup.select(".storylist > li > h4 > a"):

            if not element.has_attr("href"):
                continue

            storyURLs.append(self._baseWorkURL + element["href"])

        return storyURLs

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

        titleElement = \
            soup.select_one(".storylist .blocked h4") \
            or \
            soup.select_one(".storylist h4 a")
        if not titleElement:
            logging.error("Title element not found.")
            return False

        authorElement = soup.select_one("span.author a")
        if not authorElement:
            logging.error("Author element not found.")
            return False

        summaryElement = soup.select_one("blockquote.summary")
        if not summaryElement:
            logging.error("Summary element not found.")
            return False

        metadataElement = soup.select_one("p.meta")
        if not metadataElement:
            logging.error("Metadata element not found.")
            return False

        # Extract metadata from the description.

        metadataText = metadataElement.get_text().strip()

        chapterCountMatch = re.search("Chapters:\s*(\d+)", metadataText)

        datePublishedMatch = re.search("Published:\s*([0-9-]+)", metadataText)
        if not datePublishedMatch:
            logging.error("Date published not found.")
            return False

        dateUpdatedMatch = re.search("Updated:\s*([0-9-]+)", metadataText)

        wordCountMatch = re.search("(\d+)\s*words", metadataText)
        if not wordCountMatch:
            logging.error("Word count not found.")
            return False

        # Set the metadata.

        self.Story.Metadata.Title = titleElement.get_text().strip()
        self.Story.Metadata.Author = authorElement.get_text().strip()

        self.Story.Metadata.DatePublished = datePublishedMatch.group(1)
        self.Story.Metadata.DateUpdated = \
            dateUpdatedMatch.group(1) if dateUpdatedMatch else self.Story.Metadata.DatePublished

        self.Story.Metadata.ChapterCount = \
            int(chapterCountMatch.group(1)) if chapterCountMatch else 1
        self.Story.Metadata.WordCount = int(wordCountMatch.group(1))

        self.Story.Metadata.Summary = StripHTML(summaryElement.get_text().strip())

        # Extract chapter URLs.

        for element in soup.select("#chapters .storylist li h4 a"):

            if not element.has_attr("href"):
                continue

            self._chapterURLs.append(self._baseWorkURL + element["href"])

        if not self._chapterURLs:
            self._chapterURLs = [self.Story.Metadata.URL]

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

        titleElement = \
            soup.select_one(".storylist .blocked h4") \
            or \
            soup.select_one(".storylist h4 a")
        if not titleElement:
            logging.error("Title element not found.")
            return False

        contentElement = soup.select_one("#storytext")
        if not contentElement:
            logging.error("Content element not found.")
            return False

        # Return.

        return Chapter(
            titleElement.get_text().strip(),
            Stringify(contentElement.encode_contents())
        )

    _baseWorkURL = "https://ficwad.com"