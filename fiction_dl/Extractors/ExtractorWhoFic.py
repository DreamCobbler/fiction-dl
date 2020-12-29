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

# Standard packages.

import logging
import re
from typing import List, Optional, Tuple

# Non-standard packages.

from bs4 import BeautifulSoup, Comment, NavigableString
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

        soup = self._webSession.GetSoup(URL)
        if not soup:
            logging.error(f"Failed to download page: \"{URL}\".")
            return None

        return self._GetStoryURLsOnPage(soup)

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

        # Find additional metadata.

        datePublished, dateUpdated, summary = self._FindAdditionalMetadata(
            ExtractorWhoFic._BASE_URL + authorElement["href"],
            self._GetStoryID(URL)
        )

        # Set the metadata.

        self.Story.Metadata.Title = titleElement.get_text().strip()
        self.Story.Metadata.Author = authorElement.get_text().strip()

        self.Story.Metadata.DatePublished = datePublished
        self.Story.Metadata.DateUpdated = dateUpdated

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
    def _GetStoryID(URL: str) -> Optional[str]:

        ##
        #
        # Retrieves story ID from story URL.
        #
        # @param URL The URL of the story.
        #
        # @return The ID of the story. Optionally **None**.
        #
        ##

        if not URL:
            return None

        return FindFirstMatch(URL, "sid=(\d+)")

    def _FindAdditionalMetadata(self, authorPageURL: str, storyID: str) -> Tuple[str, str, str]:

        ##
        #
        # Reads story's publication and update dates from the author's page, as well as its summary.
        #
        # @param authorPageURL The URL of the author's profile page.
        # @param storyID       The ID of the story.
        #
        # @return A tuple consisting of date published, date updated and summary.
        #
        ##

        if (not authorPageURL) or (not storyID):
            return None

        # Prepare the default output.

        datePublished = "?"
        dateUpdated = "?"
        summary = "No summary."

        # Download the author's page soup.

        soup = self._webSession.GetSoup(authorPageURL)
        if not soup:
            return [datePublished, dateUpdated, summary]

        # Find this specific story's description.

        storyElement = None

        for storyBlockElement in soup.select("div.storyBlock"):

            anchorElement = storyBlockElement.select_one("p > strong > a")
            if (not anchorElement) or (not anchorElement.has_attr("href")):
                continue

            ID = ExtractorWhoFic._GetStoryID(anchorElement["href"])
            if not ID:
                continue

            if ID == storyID:
                storyElement = storyBlockElement
                break

        if not storyElement:
            return [datePublished, dateUpdated, summary]

        # Process the dates.

        for listItemElement in storyElement.select("ul.list-inline > li"):

            titleElement = listItemElement.select_one("b")
            if not titleElement:
                continue

            titleElementText = titleElement.get_text().strip()
            titleElement.decompose()

            if "Published:" == titleElementText:
                datePublished = listItemElement.get_text().strip()
            elif "Updated:" == titleElementText:
                dateUpdated = listItemElement.get_text().strip()

        # Process the summary.

        potentialSummaryStrings = []

        if (summaryParentElement := storyElement.select_one("p")):

            for child in summaryParentElement.children:

                if isinstance(child, NavigableString) and not isinstance(child, Comment):
                    potentialSummaryStrings.append(str(child).strip())

        if potentialSummaryStrings:
            summary = potentialSummaryStrings[-1]

        # Post-process found metadata.

        if "?" != datePublished:
            datePublished = ExtractorWhoFic._ReformatDate(datePublished)

        if "?" != dateUpdated:
            dateUpdated = ExtractorWhoFic._ReformatDate(dateUpdated)

        # Return.

        return [datePublished, dateUpdated, summary]

    @staticmethod
    def _GetStoryURLsOnPage(soup: BeautifulSoup) -> List[str]:

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

    @staticmethod
    def _ReformatDate(date: str) -> Optional[str]:

        ##
        #
        # Reformats date from YYYY.MM.DD to YYYY-MM-DD.
        #
        # @param date The input date.
        #
        # @return The input date, reformatted.
        #
        ##

        if not date:
            return None

        return date.replace(".", "-")

    _BASE_URL = "https://www.whofic.com/"