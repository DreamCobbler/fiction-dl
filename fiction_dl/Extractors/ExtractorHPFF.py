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

# Standard packages.

import logging
import re
from typing import List, Optional

# Non-standard packages.

from bs4 import BeautifulSoup
from dreamy_utilities.HTML import ReadElementText
from dreamy_utilities.Text import Stringify
from dreamy_utilities.Web import GetHostname, GetSiteURL

#
#
#
# Classes.
#
#
#

##
#
# An extractor dedicated for HarryPotterFanFiction.com.
#
##

class ExtractorHPFF(Extractor):

    def GetSupportedHostnames(self) -> List[str]:

        ##
        #
        # Returns a list of hostnames supposed to be supported by the extractor.
        #
        # @return A list of supported hostnames.
        #
        ##

        return [
            "harrypotterfanfiction.com",
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

        userIDMatch = re.search("uid=(\d+)", URL)
        if not userIDMatch:
            return None

        userID = userIDMatch.group(1)

        normalizedURL = f"{self.BASE_URL}/viewuser.php?uid={userID}"
        soup = self._webSession.GetSoup(normalizedURL)
        if not soup:
            logging.error(f"Couldn't download page: \"{normalizedURL}\".")
            return None

        storyURLs = []

        for element in soup.select("div#all-stories article.story-summary h3 a"):

            if not element.has_attr("href"):
                continue

            storyURLs.append(self.BASE_URL + element["href"])

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

        # Extract the metadata.

        titleElement = soup.select_one("div.section__content > h2")
        if not titleElement:
            logging.error("Title element not found.")
            return False

        authorElement = soup.select_one("div.section__content > h2 > i > a")
        if not authorElement:
            logging.error("Author element not found.")
            return False

        rowElements = soup.select("article.section__inner > div.row")
        if len(rowElements) < 2:
            logging.error("Failed to retrieve the second row of metadata.")
            return False

        metadataRowElement = rowElements[1]
        metadataColumnElements = metadataRowElement.select("div.col")
        if len(metadataColumnElements) < 2:
            logging.error("Found not enough columns of metadata.")
            return False

        firstColumnEntriesElements = metadataColumnElements[0].select("div.entry")
        secondColumnEntriesElements = metadataColumnElements[1].select("div.entry")
        columnEntriesElements = firstColumnEntriesElements + secondColumnEntriesElements

        chapterCountElement = None
        wordCountElement = None
        datePublishedElement = None
        dateUpdatedElement = None

        for entryElement in columnEntriesElements:

            keyElement = entryElement.select_one("div.entry__key")
            if not keyElement:
                continue

            valueElement = entryElement.select_one("div.entry__value")
            if not valueElement:
                continue

            key = keyElement.get_text().strip()

            if "Chapters" == key:
                chapterCountElement = valueElement
            elif "Words" == key:
                wordCountElement = valueElement
            elif "First Published" == key:
                datePublishedElement = valueElement
            elif "Last Updated" == key:
                dateUpdatedElement = valueElement

        if (not chapterCountElement)  or \
           (not wordCountElement)     or \
           (not datePublishedElement) or \
           (not dateUpdatedElement):
            logging.error("Some important metadata not found.")
            return False

        # Process found elements.

        author = authorElement.get_text().strip()

        titleAuthorElement = titleElement.select_one("i")
        if titleAuthorElement:
            titleAuthorElement.decompose()

        # Set the metadata.

        self.Story.Metadata.Title = titleElement.get_text().strip()
        self.Story.Metadata.Author = author

        self.Story.Metadata.DatePublished = datePublishedElement.get_text().strip()[:10]
        self.Story.Metadata.DateUpdated = dateUpdatedElement.get_text().strip()[:10]

        self.Story.Metadata.ChapterCount = int(chapterCountElement.get_text().strip())
        self.Story.Metadata.WordCount = int(wordCountElement.get_text().strip().replace(",", ""))

        self.Story.Metadata.Summary = "No summary."

        # Retrieve chapter URLs.

        chapterRowElements = soup.select("table.table-chapters > tbody > tr")
        if not chapterRowElements:
            logging.error("Chapters not found.")
            return False

        baseURL = GetSiteURL(self.Story.Metadata.URL)

        for rowElement in chapterRowElements:

            anchorElement = rowElement.select_one("td > a.h4")
            if (not anchorElement) or not anchorElement.has_attr("href"):
                logging.warning("Chapter link present, yet can't be parsed.")

            self._chapterURLs.append(f"{baseURL}{anchorElement['href']}")

        # Return.

        self.Story.URL = "https://www.google.com/"

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

        # Extract the title.

        title = None

        titleElement = soup.select_one("p.highlighted-image__title > a")
        if titleElement:
            title = titleElement.get_text().strip()

        # Extract the content.

        contentElement = soup.select_one("div.storytext-container")
        if not contentElement:
            logging.error("Could find the content element.")
            return None

        # Return.

        return Chapter(
            title = title,
            content = Stringify(contentElement.encode_contents())
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

        return f"{URL}&showRestricted"

    BASE_URL = "https://harrypotterfanfiction.com"