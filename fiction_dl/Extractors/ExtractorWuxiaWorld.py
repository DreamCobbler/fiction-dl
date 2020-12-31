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
from typing import List, Optional

# Non-standard packages.

from bs4 import BeautifulSoup
from dreamy_utilities.Text import FindFirstMatch, Stringify

#
#
#
# Classes.
#
#
#

##
#
# An extractor dedicated for WuxiaWorld.com.
#
##

class ExtractorWuxiaWorld(Extractor):

    def __init__(self) -> None:

        ##
        #
        # The constructor.
        #
        ##

        super().__init__()

        self._downloadStorySoupWhenScanning = False

    def GetSupportedHostnames(self) -> List[str]:

        ##
        #
        # Returns a list of hostnames supposed to be supported by the extractor.
        #
        # @return A list of supported hostnames.
        #
        ##

        return [
            "wuxiaworld.com",
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

        # Generate normalized URL.

        storyIdentifier = FindFirstMatch(URL, "/novel/([a-zA-Z0-9-]+)/")
        if not storyIdentifier:
            logging.error("Failed to retrieve the story identifier.")
            return False

        normalizedURL = self._BASE_NOVEL_URL + storyIdentifier
        soup = self._webSession.GetSoup(normalizedURL)
        if not soup:
            logging.error(f"Failed to download page: \"{normalizedURL}\".")
            return False

        # Locate relevant page elements.

        titleElement = soup.select_one("div.novel-body > h2")
        if not titleElement:
            logging.error("Title element not found.")
            return False

        authorElement = soup.select_one("div.novel-body > div > div > dd")
        if not authorElement:
            logging.error("Author element not found.")
            return False

        summaryElement = soup.select_one("div.novel-bottom > div > div.fr-view")
        if not summaryElement:
            logging.error("Summary element not found.")
            return False

        # Retrieve chapter URLs.

        for element in soup.select("div#chapters a"):

            if (not element.has_attr("href")) or (not element["href"].startswith("/novel/")):
                continue

            self._chapterURLs.append(self._BASE_URL + element["href"])

        # Set the metadata.

        self.Story.Metadata.Title = titleElement.get_text().strip()
        self.Story.Metadata.Author = self._ProcessAuthorName(authorElement.get_text())

        self.Story.Metadata.DatePublished = "?"
        self.Story.Metadata.DateUpdated = "?"

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

        titleElement = soup.select_one("div#chapter-outer > div.caption > div > h4")
        # No error-checking here. Not sure if every chapter has to have a title on WW.

        contentElement = soup.select_one("div#chapter-content")
        if not contentElement:
            logging.error("Content element not found.")
            return False

        # Return.

        return Chapter(
            titleElement.get_text().strip() if titleElement else "",
            Stringify(contentElement.encode_contents())
        )

    @staticmethod
    def _ProcessAuthorName(authorName: str) -> str:

        ##
        #
        # Processes author name (removes unnecessary parts).
        #
        # @param authorName The original author name, as it was retrieved.
        #
        # @return Processed author name.
        #
        ##

        if not authorName:
            return authorName

        position = authorName.find("/")
        if -1 != position:
            authorName = authorName[:position - 1]

        position = authorName.find("(")
        if -1 != position:
            authorName = authorName[:position - 1]

        return authorName.strip()

    _BASE_URL = "https://www.wuxiaworld.com"
    _BASE_NOVEL_URL = "https://www.wuxiaworld.com/novel/"