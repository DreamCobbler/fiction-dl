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
from fiction_dl.Utilities.General import Stringify
from fiction_dl.Utilities.HTML import MakeURLAbsolute
from fiction_dl.Utilities.Web import DownloadSoup, GetSiteURL

# Standard packages.

import logging
import re
import requests
from typing import List, Optional
from urllib.parse import urlparse

# Non-standard packages.

from bs4 import BeautifulSoup

#
#
#
# Classes.
#
#
#

##
#
# The extractor designed for Adult-Fanfiction.org.
#
##

class ExtractorAdultFanfiction(Extractor):

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
            "adult-fanfiction.org"
        ]

    def _InternallyScanStory(self, soup: BeautifulSoup) -> bool:

        ##
        #
        # Scans the story: generates the list of chapter URLs and retrieves the
        # metadata.
        #
        # @param soup The tag soup.
        #
        # @return **False** when the scan fails, **True** when it doesn't fail.
        #
        ##

        # Extract chapter URLs.

        normalizedURL = self._GetNormalizedStoryURL(self.Story.Metadata.URL)
        siteURL = GetSiteURL(normalizedURL)

        for linkElement in soup.select("div.dropdown-content > a"):
            self._chapterURLs.append(MakeURLAbsolute(linkElement["href"], siteURL))

        # Find the story entry in the author's profile.

        authorProfileLinkElement = soup.select_one("#contentdata tr > td > b > i > a")
        if not authorProfileLinkElement:
            logging.error("Author profile link element not found.")
            return False

        authorProfileBaseURL = authorProfileLinkElement["href"]
        zoneName = urlparse(self.Story.Metadata.URL).hostname.split(".")[0]

        authorProfileURL = f"{authorProfileBaseURL}&view=story&zone={zoneName}"
        authorProfileSoup = DownloadSoup(authorProfileURL)
        if not soup:
            logging.error(f'Failed to download page: "{authorProfileURL}".')
            return False

        authorElement = authorProfileSoup.select_one("div#contentdata > h2")
        if not authorElement:
            logging.error("Author element not found.")
            return False

        authorProfilePaginationElements = authorProfileSoup.select("div.pagination > ul > li")
        if not authorProfilePaginationElements:
            logging.error("Pagination element on author profile page not found.")
            return False

        pageCount = len(authorProfilePaginationElements)

        authorProfilePageURLs = [authorProfileURL]
        for pageIndex in range(2, pageCount + 1):
            authorProfilePageURLs.append(f"{authorProfileURL}\&page\={pageIndex}")

        matchingStoryLinkElement = None

        for URL in authorProfilePageURLs:

            authorProfileSoup = DownloadSoup(URL)
            if not soup:
                logging.error(f'Failed to download page: "{URL}".')
                return False

            for linkElement in authorProfileSoup.select("div.alist > ul > li > a"):

                if linkElement["href"].strip() == self.Story.Metadata.URL.strip():

                    matchingStoryLinkElement = linkElement.parent
                    break

            if matchingStoryLinkElement:
                break

        if not matchingStoryLinkElement:
            logging.error("Story description in the author's profile page not found.")
            return False

        matchingStoryLinkElement.select_one("a").decompose()
        storyDescriptionContent = matchingStoryLinkElement.get_text().strip()

        locatedTextPosition = storyDescriptionContent.find("Located : ")
        if -1 == locatedTextPosition:
            logging.error("Story description doesn't conform to expected format.")
            return False

        summary = storyDescriptionContent[:locatedTextPosition].strip()

        publishedMatch = re.search("Posted \: (\d\d\d\d\-\d\d\-\d\d)", storyDescriptionContent)
        if not publishedMatch:
            logging.error("Couldn't find date published in story description.")
            return False

        updatedMatch = re.search("Edited \: (\d\d\d\d\-\d\d\-\d\d)", storyDescriptionContent)
        if not updatedMatch:
            logging.error("Couldn't find date updated in story description.")
            return False

        # Set the metadata.

        self.Story.Metadata.Title = soup.select_one("h2 > a").get_text().strip()
        self.Story.Metadata.Author = authorElement.get_text().strip()

        self.Story.Metadata.DatePublished = publishedMatch.group(1).strip()
        self.Story.Metadata.DateUpdated = updatedMatch.group(1).strip()

        self.Story.Metadata.ChapterCount = len(self._chapterURLs)
        self.Story.Metadata.WordCount = 0

        self.Story.Metadata.Summary = summary

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

        rowElements = soup.select("div#contentdata > table > tr")
        if (not rowElements) or len(rowElements) < 3:
            logging.error("Chapter page doesn't conform to expected format.")

        return Chapter(
            title = None,
            content = Stringify(rowElements[2].encode_contents())
        )

    def _GetNormalizedStoryURL(self, URL: str) -> str:

        ##
        #
        # Returns a normalized story URL, i.e. one that can be used for anything.
        #
        # @param URL Input URL (given by the user).
        #
        # @return Normalized URL.
        #
        ##

        return re.sub("\&chapter\=(\d)+", "", URL)