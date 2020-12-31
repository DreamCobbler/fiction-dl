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
from fiction_dl.Utilities.HTML import MakeURLAbsolute

# Standard packages.

import logging
import re
import requests
from typing import List, Optional
from urllib.parse import urlparse

# Non-standard packages.

from bs4 import BeautifulSoup
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

        userIDMatch = re.search("profile\.php\?no=(\d+)", URL)
        if not userIDMatch:
            return None

        userID = userIDMatch.group(1)

        normalizedURL = f"http://members.adult-fanfiction.org/profile.php?no={userID}&view=story"
        soup = self._webSession.GetSoup(normalizedURL)
        if not soup:
            logging.error(f"Couldn't download page: \"{normalizedURL}\".")
            return None

        storyElements = self._FindAllStoriesByUserElements(userID)
        storyURLs = []

        for element in storyElements:

            anchorElement = element.select_one("a")
            if not anchorElement.has_attr("href"):
                continue

            storyURLs.append(anchorElement["href"])

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

        # Extract chapter URLs.

        for element in soup.select("div.dropdown-content > a"):
            self._chapterURLs.append(
                MakeURLAbsolute(element["href"],
                GetSiteURL(self._GetNormalizedStoryURL(self.Story.Metadata.URL)))
            )

        # Find the author's profile.

        userProfileAnchorElement = soup.select_one("#contentdata tr > td > b > i > a")
        if not userProfileAnchorElement:
            logging.error("Author profile link element not found.")
            return False

        userProfileBaseURL = userProfileAnchorElement["href"]
        zoneName = urlparse(self.Story.Metadata.URL).hostname.split(".")[0]

        authorProfileURL = f"{userProfileBaseURL}&view=story&zone={zoneName}"
        authorProfileSoup = self._webSession.GetSoup(authorProfileURL)
        if not soup:
            logging.error(f'Failed to download page: "{authorProfileURL}".')
            return False

        authorElement = authorProfileSoup.select_one("div#contentdata > h2")
        if not authorElement:
            logging.error("Author element not found.")
            return False

        # Find the story's entry in the author's profile.

        matchingStoryLinkElement = None

        userProfileURL = userProfileAnchorElement["href"]
        userIDMatch = re.search("profile\.php\?no=(\d+)", userProfileURL)
        if not userIDMatch:
            return None

        userID = userIDMatch.group(1)
        storyID = self._GetIDFromURL(URL)

        allStoryElements = self._FindAllStoriesByUserElements(userID)
        for element in allStoryElements:

            anchorElement = element.select_one("a")

            if self._GetIDFromURL(anchorElement["href"]) == storyID:

                matchingStoryLinkElement = anchorElement.parent
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

    def _FindAllStoriesByUserElements(self, userID):

        normalizedURL = f"http://members.adult-fanfiction.org/profile.php?no={userID}&view=story"
        soup = self._webSession.GetSoup(normalizedURL)
        if not soup:
            logging.error(f"Couldn't download page: \"{normalizedURL}\".")
            return None

        zoneNames = []

        for element in soup.select("div#contentdata > div.alistnav a"):

            if not element.has_attr("href"):
                continue

            zoneNameMatch = re.search(
                "zone=([a-zA-Z0-9]+)",
                element["href"]
            )

            if not zoneNameMatch:
                continue

            zoneNames.append(zoneNameMatch.group(1))

        storyElements = []

        for zoneName in zoneNames:

            normalizedURL = f"http://members.adult-fanfiction.org/profile.php?no={userID}&view=story&zone={zoneName}"
            soup = self._webSession.GetSoup(normalizedURL)
            if not soup:
                logging.error(f"Couldn't download page: \"{normalizedURL}\".")
                return None

            lastPageIndex = 1

            if (paginationElements := soup.select("div#contentdata > div.pagination > ul > li > a")):

                paginationElement = paginationElements[-1]

                lastPageIndexMatch = re.search("page=(\d+)", paginationElement["href"])
                lastPageIndex = int(lastPageIndexMatch.group(1))

            for pageIndex in range(1, lastPageIndex + 1):

                normalizedURL = f"http://members.adult-fanfiction.org/profile.php?no={userID}&view=story&zone={zoneName}&page={pageIndex}"
                soup = self._webSession.GetSoup(normalizedURL)
                if not soup:
                    logging.error(f"Couldn't download page: \"{normalizedURL}\".")
                    return None

                for element in soup.select("div#contentdata > div.alist > ul > li > a"):

                    storyElements.append(element.parent)

        return storyElements

    @staticmethod
    def _GetIDFromURL(URL: str) -> Optional[str]:

        ##
        #
        # Reads the story/user ID from a URL.
        #
        # @param URL The URL.
        #
        # @return The ID; optionally **None**.
        #
        ##

        if not URL:
            return None

        match = re.search(
            "no=(\d+)",
            URL
        )
        if not match:
            return None

        return match.group(1)