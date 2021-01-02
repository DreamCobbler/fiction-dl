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

        soup = self._webSession.GetSoup(URL)
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

            soup = self._webSession.GetSoup(currentURL)
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

        titleAuthorElements = soup.select("div#pagetitle a")
        if len(titleAuthorElements) < 2:
            logging.error("Title/author elements not found.")
            return False

        titleElement = titleAuthorElements[0]
        authorElement = titleAuthorElements[1]

        # Read additional metadata and retrieve chapter URLs.

        tableOfContentsURL = f"{URL}&index=1"
        soup = self._webSession.GetSoup(tableOfContentsURL)
        if not soup:
            logging.error(f"Failed to download page: \"{tableOfContentsURL}\".")
            return False

        contentElement = soup.select_one("div.listbox > div.content")
        if not contentElement:
            logging.error("Content element not found in the ToC page.")
            return False

        contentText = contentElement.get_text().strip()
        summary = FindFirstMatch(contentText, "Summary: ([^\n]+)\n")
        datePublished = FindFirstMatch(contentText, "Published:\s*([a-zA-Z]+ \d+, \d+)")
        dateUpdated = FindFirstMatch(contentText, "Updated:\s*([a-zA-Z]+ \d+, \d+)")

        for element in soup.select("div#output > p > b > a"):

            if not element.has_attr("href"):
                continue

            chapterURL = self._GetAdultViewURL(self._BASE_URL + element["href"])

            self._chapterURLs.append(chapterURL)
            self._chapterTitles[chapterURL] = element.get_text().strip()

        if not self._chapterURLs:
            logging.error("No chapters found.")
            return False

        # Set the metadata.

        self.Story.Metadata.Title = titleElement.get_text().strip()
        self.Story.Metadata.Author = authorElement.get_text().strip()

        self.Story.Metadata.DatePublished = self._ReformatDate(datePublished) or "?"
        self.Story.Metadata.DateUpdated = self._ReformatDate(dateUpdated) or "?"

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

        return self._GetAdultViewURL(URL)

    def _GetAdultViewURL(self, URL: str) -> Optional[str]:

        ##
        #
        # Returns a URL leading to the page, this time with adult-mode enabled.
        #
        # @param URL Page URL.
        #
        # @return The adult-proofed URL.
        #
        ##

        if not URL:
            return None

        MINIMUM_WARNING = 1
        MAXIMUM_WARNING = 5

        for warningIndex in reversed(range(MINIMUM_WARNING, MAXIMUM_WARNING + 1)):

            currentURL = URL + f"&ageconsent=ok&warning={warningIndex}"
            soup = self._webSession.GetSoup(currentURL)

            if not soup.select_one("div.errortext"):
                return currentURL

        return URL + "&ageconsent=ok"

    @staticmethod
    def _ReformatDate(date: str) -> Optional[str]:

        ##
        #
        # Reformats long date format to standard format.
        #
        # @param date The input date, as read on the webpage.
        #
        # @return ISO-formatted date. Optionally **None**.
        #
        ##

        if not date:
            return None

        try:

            return datetime.strptime(date, "%b %d, %Y").strftime("%Y-%m-%d")

        except ValueError:

            return None

    _BASE_URL = "http://samandjack.net/fanfics/"
    _STORIES_PER_PAGE = 25