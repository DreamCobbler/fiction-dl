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

from datetime import datetime
import logging
import re
from typing import List, Optional

# Non-standard packages.

from bs4 import BeautifulSoup
from dreamy_utilities.Text import Stringify
from dreamy_utilities.Web import GetHostname

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

        # Download author's profile page.

        userIDMatch = re.search("\?uid\=(\d+)", URL)
        if not userIDMatch:
            return None

        userID = userIDMatch.group(1)
        userPageURL = f"{self.MEMBER_PAGE_URL}uid={userID}&page=submissions"

        soup = self._webSession.GetSoup(userPageURL)
        if not soup:
            return None

        # Locate all the stories.

        storyURLs = []

        storyHeaderElement = soup.select_one("tr.st-top")
        if not storyHeaderElement:
            return None

        storyRowElement = storyHeaderElement.next_sibling
        while storyRowElement:

            if not storyRowElement.has_attr("class"):
                break

            if "root-story" in storyRowElement["class"]:

                anchorElement = storyRowElement.select_one("a")
                if (not anchorElement) or (not anchorElement.has_attr("href")):
                    continue

                storyURLs.append(anchorElement["href"])
                storyRowElement = storyRowElement.next_sibling

            elif "ser-ttl" in storyRowElement["class"]:

                storyRowElement = storyRowElement.next_sibling
                if (not storyRowElement.has_attr("class")) or ("sl" not in storyRowElement["class"]):
                    continue

                anchorElement = storyRowElement.select_one("a")
                if (not anchorElement) or (not anchorElement.has_attr("href")):
                    continue

                storyURLs.append(anchorElement["href"])
                storyRowElement = storyRowElement.next_sibling

            elif "sl" in storyRowElement["class"]:

                storyRowElement = storyRowElement.next_sibling

            else:

                break

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
        authorsPageSoup = self._webSession.GetSoup(authorsPageURL)
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

        # Prepare metadata.

        title = titleElement.get_text().strip()
        datePublished = self._ReformatDate(publishedElement.get_text().strip())
        dateUpdated = self._ReformatDate(publishedElement.get_text().strip())

        # Check if the story belongs to a series.

        seriesRowElement = None

        if storyRowElement.has_attr("class") and ("sl" in storyRowElement["class"]):

            seriesRowElement = storyRowElement.find_previous_sibling(
                "tr",
                {"class": "ser-ttl"}
            )

        if seriesRowElement:

            title = seriesRowElement.get_text().strip()
            chapterDates = []

            seriesChapterRowElement = seriesRowElement.next_sibling
            while seriesChapterRowElement:

                if (not seriesChapterRowElement.has_attr("class")) or ("sl" not in seriesChapterRowElement["class"]):
                    break

                seriesChapterAnchorElement = seriesChapterRowElement.select_one("a")
                if (not seriesChapterAnchorElement) or (not seriesChapterAnchorElement.has_attr("href")):
                    break

                seriesChapterCellElements = seriesChapterRowElement.select("td")
                if seriesChapterCellElements:
                    chapterDates.append(seriesChapterCellElements[-1].get_text().strip())

                self._chapterURLs.append(seriesChapterAnchorElement["href"])
                seriesChapterRowElement = seriesChapterRowElement.next_sibling

            datePublished = self._ReformatDate(chapterDates[0])
            dateUpdated = self._ReformatDate(chapterDates[-1])

        else:

            self._chapterURLs = [self.Story.Metadata.URL]

        # Set the metadata.

        self.Story.Metadata.Title = title
        self.Story.Metadata.Author = authorElement.get_text().strip()

        self.Story.Metadata.DatePublished = datePublished
        self.Story.Metadata.DateUpdated = dateUpdated

        self.Story.Metadata.ChapterCount = len(self._chapterURLs)
        self.Story.Metadata.WordCount = 0

        self.Story.Metadata.Summary = StripHTML(summaryElement.get_text()).strip()

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

            pageURL = URL + f"?page={pageIndex}"

            soup = self._webSession.GetSoup(pageURL)
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

        if not date:
            return None

        return datetime.strptime(date, "%m/%d/%y").strftime("%Y-%m-%d")

    MEMBER_PAGE_URL = "https://www.literotica.com/stories/memberpage.php?"