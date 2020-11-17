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
from dreamy_utilities.Containers import RemoveDuplicates
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
# An extractor dedicated for WhoFic.com.
#
##

class ExtractorWhoFic(Extractor):

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
            "whofic.com",
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

        if ("seriesid" not in URL) and ("viewuser.php" not in URL):
            return None

        soup = DownloadSoup(URL)
        if not soup:
            logging.error(f"Couldn't download page: \"{URL}\".")
            return None

        storyURLs = self._GetStoryLinksOnPage(soup)

        for element in soup.select("div.box > div.seriesBlock > p > strong > a"):

            if not element.has_attr("href"):
                continue

            seriesIDMatch = re.search(
                "seriesid=(\d+)",
                element["href"]
            )

            if not seriesIDMatch:
                continue

            seriesID = seriesIDMatch.group(1)
            seriesURL = f"{self._BASE_URL}series.php?seriesid={seriesID}"

            soup = DownloadSoup(seriesURL)
            if not soup:
                logging.error(f"Couldn't download page: \"{seriesURL}\".")
                continue

            newURLs = self._GetStoryLinksOnPage(soup)
            storyURLs.extend(newURLs)

        storyURLs = RemoveDuplicates(storyURLs)

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

        titleElement = soup.select_one("div#storyHeader > h1")
        if not titleElement:
            logging.error("Title element not found.")
            return False

        authorElement = soup.select_one("div#storyHeader > p.mb-0 > a")
        if not authorElement:
            logging.error("Author element not found.")
            return False

        # Extract chapter URLs.

        for element in soup.select("div.container > div.row > div.box > p > b > a"):

            if not element.has_attr("href"):
                continue

            self._chapterURLs.append(self._BASE_URL + element["href"])

        if not self._chapterURLs:
            self._chapterURLs.append(URL)

        # Set the metadata.

        self.Story.Metadata.Title = titleElement.get_text().strip()
        self.Story.Metadata.Author = authorElement.get_text().strip()

        self.Story.Metadata.DatePublished = "?"
        self.Story.Metadata.DateUpdated = "?"

        self.Story.Metadata.ChapterCount = len(self._chapterURLs)
        self.Story.Metadata.WordCount = 0

        self.Story.Metadata.Summary = "No summary."

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

        contentElement = soup.select_one("div.container > div.row > div.box")
        if not contentElement:
            logging.error("Content element not found.")
            return False

        if (element := contentElement.select_one("div#storyHeader")):
            element.decompose()

        if (element := contentElement.select_one("div#authorNotes")):
            element.decompose()

        for element in contentElement.select("form"):
            element.decompose()

        # Return.

        return Chapter(
            content = Stringify(contentElement.encode_contents())
        )

    @staticmethod
    def _GetStoryLinksOnPage(soup: BeautifulSoup) -> List[str]:

        ##
        #
        # Reads all the story links present on a specific page.
        #
        # @param soup The input tag soup.
        #
        # @return A list of (absolute) story URLs.
        #
        ##

        URLs = []

        for element in soup.select("div.box > div.storyBlock > p > strong > a"):

            if not element.has_attr("href"):
                continue

            storyIDMatch = re.search(
                "sid=(\d+)",
                element["href"]
            )

            if not storyIDMatch:
                continue

            storyID = storyIDMatch.group(1)
            storyURL = f"{ExtractorWhoFic._BASE_URL}viewstory.php?sid={storyID}"

            URLs.append(storyURL)

        return URLs

    _BASE_URL = "https://www.whofic.com/"