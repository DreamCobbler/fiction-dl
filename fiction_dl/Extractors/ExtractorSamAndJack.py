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

import logging
import re
from typing import List, Optional

# Non-standard packages.

from bs4 import BeautifulSoup
from dreamy_utilities.Filesystem import WriteTextFile
from dreamy_utilities.HTML import ReadElementText
from dreamy_utilities.Text import Stringify
from dreamy_utilities.Web import DownloadSoup, GetHostname, GetSiteURL

#
#
#
# Classes.
#
#
#

##
#
# An extractor dedicated for SamAndJack.net.
#
##

class ExtractorSamAndJack(Extractor):

    def __init__(self) -> None:

        ##
        #
        # The constructor.
        #
        ##

        super().__init__()

        self._chapterTitles = {}

    def GetSupportedHostnames(self) -> List[str]:

        ##
        #
        # Returns a list of hostnames supposed to be supported by the extractor.
        #
        # @return A list of supported hostnames.
        #
        ##

        return [
            "samandjack.net",
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

        if "viewuser.php" not in URL:
            return None

        soup = DownloadSoup(URL)
        if not soup:
            logging.error(f"Couldn't download page: \"{URL}\".")
            return None

        # Get the number of pages.

        pageCount = 1

        if (pageLinksElement := soup.select_one("#pagelinks")):

            linkElements = pageLinksElement.select("a")
            if len(linkElements):
                pageCount = len(linkElements) - 1

        # Scan stories on every page.

        storyURLs = []

        for pageIndex in range(1, pageCount + 1):

            currentOffset = (pageIndex - 1) * self._STORIES_PER_PAGE
            currentURL = f"{URL}&offset={currentOffset}"

            soup = DownloadSoup(currentURL)
            if not soup:
                continue

            for element in soup.select("td.main div.listbox div.title"):

                linkElement = element.select_one("a")
                if (not linkElement) or (not linkElement.has_attr("href")):
                    continue

                storyIDMatch = re.search(
                    "sid=(\d+)",
                    linkElement["href"]
                )

                if not storyIDMatch:
                    continue

                storyID = storyIDMatch.group(1)
                storyURL = f"{self._BASE_URL}viewstory.php?sid={storyID}"

                storyURLs.append(storyURL)

        # Return.

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

        # WriteTextFile("test.html", str(soup))

        titleAuthorElements = soup.select("div#pagetitle a")
        if len(titleAuthorElements) < 2:
            logging.error("Title/author elements not found.")
            return False

        titleElement = titleAuthorElements[0]
        authorElement = titleAuthorElements[1]

        # Retrieve chapter URLs.

        tableOfContentsURL = f"{URL}&index=1"

        soup = DownloadSoup(tableOfContentsURL)
        if not soup:
            logging.error(f"Failed to download page: \"{tableOfContentsURL}\".")
            return False

        for element in soup.select("div#output > p > b > a"):

            if not element.has_attr("href"):
                continue

            chapterURL = self._BASE_URL + element["href"]

            self._chapterURLs.append(chapterURL)
            self._chapterTitles[chapterURL] = element.get_text().strip()

        if not self._chapterURLs:
            logging.error("No chapters found.")
            return False

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

        # Extract the content.

        contentElement = soup.select_one("div#story")
        if not contentElement:
            logging.error("Couldn't find the content element.")
            return None

        # Return.

        return Chapter(
            title = self._chapterTitles[URL] if (URL in self._chapterTitles) else None,
            content = Stringify(contentElement.encode_contents())
        )

    def _GetNormalizedStoryURL(self, URL: str) -> Optional[str]:

        ##
        #
        # Returns a normalized story URL, i.e. one that can be used for anything.
        #
        # @param URL Input URL (given by the user).
        #
        # @return Normalized URL.
        #
        ##

        return URL + "&ageconsent=ok&warning=5"

    _BASE_URL = "http://samandjack.net/fanfics/"
    _STORIES_PER_PAGE = 25