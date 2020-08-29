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
from fiction_dl.Utilities.General import Stringify
from fiction_dl.Utilities.HTML import StripHTML
from fiction_dl.Utilities.Text import IsStringTrulyEmpty
from fiction_dl.Utilities.Web import DownloadSoup, GetHostname

# Standard packages.

from datetime import datetime
import logging
import re
import requests
from typing import List, Optional

# Non-standard packages.

from bs4 import BeautifulSoup

###
#
#
# Extractor designed to work for literotica.com.
#
#
###

class ExtractorLiterotica(Extractor):

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
            "literotica.com"
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

        userIDMatch = re.search("\?uid\=(\d+)", URL)
        if not userIDMatch:
            return None

        userID = userIDMatch.group(1)
        normalizedURL = \
            f"https://www.literotica.com/stories/memberpage.php?uid={userID}&page=submissions"

        pageSoup = DownloadSoup(normalizedURL)
        if not pageSoup:
            return None

        storyURLs = []

        storyElements = pageSoup.find_all("tr", {"class": "root-story"})
        storyElements.extend(pageSoup.find_all("tr", {"class": "sl"}))

        for storyElement in storyElements:

            anchorElement = storyElement.find("a")
            if (not anchorElement) or (not anchorElement.has_attr("href")):
                logging.error("Failed to retrieve story URL from the Submissions webpage.")
                continue

            storyURLs.append(anchorElement["href"])

        return storyURLs

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

        # Extract basic metadata.

        titleElement = soup.select_one("div.b-story-header > h1")
        if not titleElement:
            logging.error("Title element not found.")
            return False

        authorElement = soup.select_one("div.b-story-header > span.b-story-user-y > a")
        if not authorElement:
            logging.error("Author element not found.")
            return False

        # Download the author's page.

        if not authorElement.has_attr("href"):
            logging.error("Can't find the URL of the author's page.")
            return False

        authorsPageURL = authorElement["href"]
        authorsPageSoup = DownloadSoup(authorsPageURL)
        if not authorsPageSoup:
            logging.error(f'Failed to download page: "{authorsPageURL}".')
            return False

        # Extract remaining metadata.

        storyRowElement = None

        for storyLinkElement in authorsPageSoup.select("td.fc > a"):
            if storyLinkElement.get_text().strip() == titleElement.get_text().strip():
                storyRowElement = storyLinkElement.parent.parent
                break

        if not storyRowElement:
            logging.error("Failed to find the story's entry on the author's page.")
            return False

        storyMetadataElements = storyRowElement.find_all("td")
        if len(storyMetadataElements) < 4:
            logging.error("Can't extract metadata from the author's page.")
            return False

        summaryElement = storyMetadataElements[1]
        publishedElement = storyMetadataElements[3]

        # Set the metadata.

        self.Story.Metadata.Title = titleElement.get_text().strip()
        self.Story.Metadata.Author = authorElement.get_text().strip()

        self.Story.Metadata.DatePublished = self._ReformatDate(publishedElement.get_text().strip())
        self.Story.Metadata.DateUpdated = self.Story.Metadata.DatePublished

        self.Story.Metadata.ChapterCount = 1
        self.Story.Metadata.WordCount = 0

        self.Story.Metadata.Summary = StripHTML(summaryElement.get_text()).strip()

        # "Extract" chapter URLs.

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

        # Find the page count of the story.

        pageCount = 1

        if (pageSelectElement := soup.find("select", {"name": "page"})):

            pageCount = len(pageSelectElement.find_all("option"))

            if pageCount < 1:

                logging.error("Failed to read the story's page count.")
                return None

        # Iterate over pages and read their content.

        content = ""

        for pageIndex in range(1, pageCount + 1):

            pageURL = self.Story.Metadata.URL + f"?page={pageIndex}"

            soup = DownloadSoup(pageURL)
            if not soup:
                logging.error(f'Failed to download page: "{pageURL}".')
                return None

            contentElement = soup.select_one("div.b-story-body-x > div")
            if not contentElement:
                logging.error("Story content element not found.")
                return None

            content += "<br/><br/>" + Stringify(contentElement.encode_contents())

        # Return.

        return Chapter(
            title = None,
            content = content
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

        if not URL:
            return URL

        argumentPosition = URL.find("?")
        if -1 != argumentPosition:
            URL = URL[:argumentPosition]

        return URL

    @staticmethod
    def _ReformatDate(date: str) -> Optional[str]:

        ##
        #
        # Reformats date to ISO 8601.
        #
        # @param date The date in Literotica format (mm/dd/yy).
        #
        # @return The date in ISO 8601 format.
        #
        ##

        if IsStringTrulyEmpty(date):
            return None

        return datetime.strptime(date, "%m/%d/%y").strftime("%Y-%m-%d")