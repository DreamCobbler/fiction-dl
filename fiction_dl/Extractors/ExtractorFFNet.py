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
from fiction_dl.Utilities.General import GetCurrentDate, Stringify
from fiction_dl.Utilities.HTML import StripHTML
from fiction_dl.Utilities.Web import DownloadSoup, GetHostname, GetSiteURL

# Standard packages.

from datetime import datetime
import logging
import re
from typing import List, Optional

# Non-standard packages.

from bs4 import BeautifulSoup

#
#
#
# The class definition.
#
#
#

class ExtractorFFNet(Extractor):


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
            "fanfiction.net",
            "fictionpress.com"
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

        userIDMatch = re.search("/u/(\d+)", URL)
        if not userIDMatch:
            return None

        userID = userIDMatch.group(1)

        siteURL = GetSiteURL(URL)
        normalizedURL = f"{siteURL}/u/{userID}/"

        pageSoup = DownloadSoup(normalizedURL)
        if not pageSoup:
            return None

        storyIDs = []

        storyElements = pageSoup.find_all("div", {"class": "mystories"})
        for element in storyElements:

            linkElement = element.find("a", {"class": "stitle"})
            if (not linkElement) or (not linkElement.has_attr("href")):
                logging.error("Failed to retrieve story URL.")
                continue

            storyIDMatch = re.search("/s/(\d+)", linkElement["href"])
            if not storyIDMatch:
                logging.error("Failed to retrieve story ID from its URL.")
                continue

            storyID = storyIDMatch.group(1)
            storyIDs.append(storyID)

        storyURLs = [f"{siteURL}/s/{ID}/" for ID in storyIDs]
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

        # Extract metadata.

        headerElement = soup.find(id = "profile_top")
        if not headerElement:
            logging.error("Header element not found.")
            return False

        headerLines = headerElement.get_text().replace("Follow/Fav", "").split("\n")

        chapterCount = re.search("Chapters: (\d+)", headerLines[3])
        # If the story has just one chapter, this field won't be present.

        words = re.search("Words: ([\d,]+)", headerLines[3])
        if not words:
            logging.error("Word count field not found in header.")
            return False

        datePublished = re.search("Published: ([\d//]+)", headerLines[3])
        if not datePublished:
            logging.error("Date published field not found in header.")
            return False

        dateUpdated = re.search("Updated: ([\d//]+)", headerLines[3])
        # If the story has just one chapter, this field won't be present.

        # Set the metadata.

        self.Story.Metadata.Title = headerLines[0].strip()
        self.Story.Metadata.Author = headerLines[1][4:].strip() # Removes the "By: " part.
        self.Story.Metadata.Summary = StripHTML(headerLines[2]).strip()

        self.Story.Metadata.DatePublished = self._ReformatDate(datePublished.group(1))
        self.Story.Metadata.DateUpdated = (
            self._ReformatDate(dateUpdated.group(1))
            if dateUpdated else
            self.Story.Metadata.DatePublished
        )

        self.Story.Metadata.ChapterCount = int(chapterCount.group(1)) if chapterCount else 1
        self.Story.Metadata.WordCount = int(words.group(1).replace(",", ""))

        # Retrieve chapter URLs.

        storyID = self._GetStoryID(self.Story.Metadata.URL)
        if not storyID:
            logging.error("Failed to retrieve story ID from URL.")
            return False

        baseURL = GetSiteURL(self.Story.Metadata.URL)
        for index in range(1, self.Story.Metadata.ChapterCount + 1):
            self._chapterURLs.append(f"{baseURL}/s/{storyID}/{index}/")

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

        # Read the title.

        title = None

        if (selectedChapterElement := soup.find("option", {"selected": True})):
            title = selectedChapterElement.text.strip()

        if title and (titleMatch := re.search("\d+\. (.*)", title)):
            title = titleMatch.group(1)

        # Read the content.

        storyTextElement = soup.find(id = "storytext")
        if not storyTextElement:
            logging.error("Story text element not found.")
            return None

        # Create the Chapter and return it.

        return Chapter(
            title = title,
            content = Stringify(storyTextElement.encode_contents())
        )

    @staticmethod
    def _GetStoryID(URL: str) -> Optional[str]:

        if not URL:
            return None

        storyIDMatch = re.search("/s/(\d+)/", URL)
        if not storyIDMatch:
            return None

        return storyIDMatch.group(1)

    @staticmethod
    def _ReformatDate(date: str) -> Optional[str]:

        if not date:
            return None

        try:

            # Dates on FF.net come in two formats: "m/d/yyyy" and "m/d".
            # We want to convert the shorter format to the longer one.

            longDatePattern = re.compile("^\d+/\d+/\d+$")

            if not longDatePattern.match(date):
                date += f"/{datetime.now().year}"

            # And then the longer format to the standard format.

            date = datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d")

            return date

        except ValueError:

            return GetCurrentDate()