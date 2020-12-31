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
from dreamy_utilities.Interface import Interface
from dreamy_utilities.Text import DeprettifyAmount, DeprettifyNumber, Stringify
from dreamy_utilities.Web import GetHostname

#
#
#
# The class definition.
#
#
#

class ExtractorAO3(Extractor):

    def __init__(self) -> None:

        ##
        #
        # The constructor.
        #
        ##

        super().__init__()

        self._storySoup = None

    def SupportsAuthentication(self) -> bool:

        ##
        #
        # Checks whether the extractor supports user authentication.
        #
        # @return **True** if the site *does* support authentication, **False** otherwise.
        #
        ##

        return True

    def Authenticate(self, interface: Interface) -> bool:

        ##
        #
        # Logs the user in, interactively.
        #
        # @param interface The user interface to be used.
        #
        # @return **True** if the user has been authenticated correctly, **False** otherwise.
        #
        ##

        # Download the log-in page.

        soup = self._webSession.GetSoup(self._LOGIN_URL)
        if not soup:
            logging.error("Failed to download the log-in page.")
            return self.AuthenticationResult.FAILURE

        formElement = soup.select_one("form#new_user_session_small")
        if not formElement:
            logging.error("Log-in form element not found.")
            return self.AuthenticationResult.FAILURE

        authenticityTokenElement = formElement.find("input", {"name": "authenticity_token"})
        if not authenticityTokenElement:
            logging.error("\"authenticity_token\" input field not found.")
            return self.AuthenticationResult.FAILURE
        elif not authenticityTokenElement.has_attr("value"):
            logging.error("\"authenticity_token\" input field doesn't have a value.")
            return self.AuthenticationResult.FAILURE

        authenticityToken = authenticityTokenElement["value"].strip()

        # Read the username and the password.

        userName = ""
        password = ""

        if ExtractorAO3._userName is None:

            interface.GrabUserAttention()

            userName = interface.ReadString("Your username")
            if userName:
                password = interface.ReadPassword("Your password")

        else:

            userName = ExtractorAO3._userName
            password = ExtractorAO3._userPassword

        if not userName:
            userName = ""

        # Remember the username and the password.

        ExtractorAO3._userName = userName
        ExtractorAO3._userPassword = password

        # Decide whether to log-in.

        if (not userName) or (not password):
            return self.AuthenticationResult.ABANDONED

        # Attempt to log-in.

        data = {
            "user[login]": userName,
            "user[password]": password,
            "user[remember_me]": "1",
            "authenticity_token": authenticityToken,
        }

        response = self._session.post(
            url = self._LOGIN_URL,
            data = data
        )

        # Verify the response and return.

        if (200 != response.status_code) or ("doesn't match our records" in response.text.lower()):
            return self.AuthenticationResult.FAILURE

        return self.AuthenticationResult.SUCCESS

    def GetSupportedHostnames(self) -> List[str]:

        ##
        #
        # Returns a list of hostnames supposed to be supported by the extractor.
        #
        # @return A list of supported hostnames.
        #
        ##

        return [
            "archiveofourown.org"
        ]

    def RequiresBreaksBetweenRequests(self) -> bool:

        ##
        #
        # Does the extractor require the application to sleep between subsequent reqests?
        #
        # @return **True** if it does, **False** otherwise.
        #
        ##

        return False

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

        seriesMatch = re.search("/series/([a-zA-Z0-9_]+)", URL)
        if seriesMatch:
            return self._ScanWorks(f"{self._BASE_SERIES_URL}/{seriesMatch.group(1)}")

        collectionMatch = re.search("/collections/([a-zA-Z0-9_]+)", URL)
        if collectionMatch:
            return self._ScanWorks(f"{self._BASE_COLLECTION_URL}/{collectionMatch.group(1)}/works")

        usernameMatch = re.search("/users/([a-zA-Z0-9_]+)", URL)
        if usernameMatch:
            return self._ScanWorks(f"{self._BASE_USER_URL}/{usernameMatch.group(1)}/works")

        return None

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

        # Store the tag soup.

        self._storySoup = soup

        # Extract the metadata.

        self.Story.Metadata.Title = ReadElementText(self._storySoup, "h2.title")
        self.Story.Metadata.Author = ReadElementText(self._storySoup, "a[rel~=author]") or "Anonymous"

        self.Story.Metadata.DatePublished = ReadElementText(self._storySoup, "dd.published")
        self.Story.Metadata.DateUpdated = ReadElementText(self._storySoup, "dd.status") or self.Story.Metadata.DatePublished

        chapterCount = DeprettifyAmount(ReadElementText(self._storySoup, "dd.chapters"))[0]

        self.Story.Metadata.ChapterCount = DeprettifyAmount(ReadElementText(self._storySoup, "dd.chapters"))[0]
        self.Story.Metadata.WordCount = DeprettifyNumber(ReadElementText(self._storySoup, "dd.words"))

        self.Story.Metadata.Summary = ReadElementText(self._storySoup, "blockquote.userstuff") or "No summary."

        # Validate story metadata.

        if (missingMetadata := self.Story.Metadata.AreValuesMissing()):

            logging.error(f"Failed to read following story metadata: {', '.join(missingMetadata)}.")

            return False

        # Return.

        return True

    def ExtractChapter(self, index: int) -> Optional[Chapter]:

        ##
        #
        # Extracts specific chapter.
        #
        # @param index The index of the chapter to be extracted.
        #
        # @return **True** if the chapter is extracted correctly, **False** otherwise.
        #
        ##

        if 1 == self.Story.Metadata.ChapterCount:

            titleElement = None

            contentElement = self._storySoup.select_one("div#chapters div.userstuff")
            if not contentElement:
                logging.error("Content element not found.")
                return None

            if (landmarkElement := contentElement.select_one("h3#work")):
                landmarkElement.decompose()

            return Chapter(
                title = titleElement.get_text().strip() if titleElement else None,
                content = Stringify(contentElement.encode_contents())
            )

        else:

            chapterElements = self._storySoup.select("div#chapters > div.chapter")
            if index > len(chapterElements):
                logging.error(
                    f"Trying to extract chapter {index}. "
                    f"Only {len(chapterElements)} chapter(s) located. "
                    f"The story supposedly has {self.Story.Metadata.ChapterCount} chapter(s)."
                )
                return None

            currentChapterElement = chapterElements[index - 1]

            titleElement = currentChapterElement.select_one("h3.title")
            contentElement = currentChapterElement.select_one("div.userstuff")

            if (landmarkElement := contentElement.select_one("h3#work")):
                landmarkElement.decompose()

            return Chapter(
                title = titleElement.get_text().strip() if titleElement else None,
                content = Stringify(contentElement.encode_contents())
            )

    def _ScanWorks(self, URL: str) -> Optional[List[str]]:

        ##
        #
        # Scans a list of works: generates the list of story URLs.
        #
        # @param URL The URL.
        #
        # @return **None** when the scan fails, a list of story URLs when it doesn't fail.
        #
        ##

        # Check the arguments.

        if not URL:
            return None

        # Download page soup.

        soup = self._webSession.GetSoup(URL)
        if not soup:
            return None

        # Locate all the pages of the list.

        pageURLs = []

        if not (paginationElement := soup.find("ol", {"title": "pagination"})):

            pageURLs.append(URL)

        else:

            pageButtonElements = paginationElement.find_all("li")
            pageCount = len(pageButtonElements) - 2

            if pageCount < 1:
                logging.error("Invalid number of pages on the Works webpage.")
                return None

            for index in range(1, pageCount + 1):
                pageURLs.append(f"{URL}?page={index}")

        # Read all the stories on all the pages.

        storyURLs = []

        for pageURL in pageURLs:

            soup = self._webSession.GetSoup(pageURL)
            if not soup:
                logging.error("Failed to download a page of the Works webpage.")
                continue

            for storyElement in soup.select("li.work"):

                linkElement = storyElement.find("a")
                if (not linkElement) or (not linkElement.has_attr("href")):
                    logging.error("Failed to retrieve story URL from the Works webpage.")
                    continue

                storyID = ExtractorAO3._GetStoryID(linkElement["href"])
                if not storyID:
                    logging.error("Failed to retrieve story ID from its URL.")
                    continue

                storyURLs.append(f"{ExtractorAO3._BASE_WORK_URL}/{storyID}")

        # Return.

        return storyURLs

    @staticmethod
    def _GetNormalizedStoryURL(URL: str) -> Optional[str]:

        ##
        #
        # Returns a normalized story URL, i.e. one that can be used for anything.
        #
        # @param URL Input URL.
        #
        # @return Normalized URL.
        #
        ##

        if not URL:
            return None

        return ExtractorAO3._GetAdultFullStoryURL(
            f"{ExtractorAO3._BASE_WORK_URL}/{ExtractorAO3._GetStoryID(URL)}"
        )

    @staticmethod
    def _GetPrettyStoryURL(URL: str) -> Optional[str]:

        ##
        #
        # Returns a "pretty" story URL, i.e. one that can be used for printing in story content.
        #
        # @param URL Input URL (given by the user).
        #
        # @return Pretty URL.
        #
        ##

        if not URL:
            return None

        return f"{ExtractorAO3._BASE_WORK_URL}/{ExtractorAO3._GetStoryID(URL)}"

    @staticmethod
    def _GetAdultFullStoryURL(URL: str) -> Optional[str]:

        ##
        #
        # Returns a URL leading to the page containg the whole story content, with adult-mode
        # enabled.
        #
        # @param URL Story URL.
        #
        # @return The code of the page containing the whole work.
        #
        ##

        if not URL:
            return None

        return URL + "?view_adult=true&view_full_work=true"

    @staticmethod
    def _GetStoryID(URL: str) -> Optional[str]:

        ##
        #
        # Retrieves story ID from story URL.
        #
        # @param URL Story URL.
        #
        # @return Story ID.
        #
        ##

        if not URL:
            return None

        storyIDMatch = re.search("/works/(\d+)", URL)
        if not storyIDMatch:
            return None

        return storyIDMatch.group(1)

    _userName = None
    _userPassword = None

    _LOGIN_URL = "https://archiveofourown.org/users/login"
    _BASE_WORK_URL = "https://archiveofourown.org/works"
    _BASE_USER_URL = "https://archiveofourown.org/users"
    _BASE_SERIES_URL = "https://archiveofourown.org/series"
    _BASE_COLLECTION_URL = "https://archiveofourown.org/collections"