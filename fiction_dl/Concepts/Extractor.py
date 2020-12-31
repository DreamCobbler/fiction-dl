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
from fiction_dl.Concepts.Story import Story
import fiction_dl.Configuration as Configuration

# Standard packages.

from enum import Enum
import logging
import requests
from typing import List, Optional

# Non-standard packages.

from bs4 import BeautifulSoup
from dreamy_utilities.Interface import Interface
from dreamy_utilities.Web import GetHostname
from dreamy_utilities.WebSession import WebSession
from fake_useragent import UserAgent

#
#
#
# Classes.
#
#
#

##
#
# An abstract extractor, meant to be inherited from. Represents a concept of a
# tool capable of handling content coming from a specific source.
#
##

class Extractor:

    ##
    #
    # Represents authentication result.
    #
    ##

    class AuthenticationResult(Enum):
        SUCCESS   = 1
        FAILURE   = 2
        ABANDONED = 3

    def __init__(self) -> None:

        ##
        #
        # The constructor.
        #
        ##

        self.Story = None

        self._webSession = WebSession(UserAgent().random)
        self._chapterURLs = []

        self._downloadStorySoupWhenScanning = True
        self._downloadChapterSoupWhenExtracting = True

        self._chapterParserName = "html.parser"

    def GetSupportedHostnames(self) -> List[str]:

        ##
        #
        # Returns a list of hostnames supposed to be supported by the extractor.
        #
        # @return A list of supported hostnames.
        #
        ##

        return []

    def RequiresBreaksBetweenRequests(self) -> bool:

        ##
        #
        # Does the extractor require the application to sleep between subsequent reqests?
        #
        # @return **True** if it does, **False** otherwise.
        #
        ##

        return True

    def SupportsAuthentication(self) -> bool:

        ##
        #
        # Checks whether the extractor supports user authentication.
        #
        # @return **True** if the site *does* support authentication, **False** otherwise.
        #
        ##

        return False

    def Authenticate(self, interface: Interface) -> AuthenticationResult:

        ##
        #
        # Logs the user in, interactively.
        #
        # @param interface The user interface to be used.
        #
        # @return The result of the authentication attempt.
        #
        ##

        return AuthenticationResult.FAILURE

    def Initialize(self, URL: str) -> bool:

        ##
        #
        # Initializes the extractor with given URL.
        #
        # @param URL The URL in question.
        #
        # @return **True** if the extractor can handle the URL, **False** otherwise.
        #
        ##

        if GetHostname(URL) not in self.GetSupportedHostnames():
            return False

        self.Story = Story(self._GetPrettyStoryURL(URL))

        return True

    def ScanChannel(self, URL: str) -> Optional[List[str]]:

        ##
        #
        # Scans the channel: generates the list of story URLs.
        #
        # @return **None** when the scan fails, a list of story URLs when it doesn't fail.
        #
        ##

        return None

    def ScanStory(self) -> bool:

        ##
        #
        # Scans the story: generates the list of chapter URLs and retrieves the
        # metadata.
        #
        # @return **False** when the scan fails, **True** when it doesn't fail.
        #
        ##

        if self.Story is None:
            logging.error("The extractor isn't initialized.")
            return False

        normalizedURL = self._GetNormalizedStoryURL(self.Story.Metadata.URL)

        soup = None

        if self._downloadStorySoupWhenScanning:

            soup = self._webSession.GetSoup(normalizedURL)

            if not soup:
                logging.error(f'Failed to download tag soup: "{normalizedURL}".')
                return False

        return self._InternallyScanStory(normalizedURL, soup)

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

        if index > len(self._chapterURLs):
            logging.error(
                f"Trying to extract chapter {index}. "
                f"Only {len(self._chapterURLs)} chapter(s) located. "
                f"The story supposedly has {self.Story.Metadata.ChapterCount} chapter(s)."
            )
            return None

        chapterURL = self._chapterURLs[index - 1]

        soup = None

        if self._downloadChapterSoupWhenExtracting:

            soup = self._webSession.GetSoup(chapterURL, self._chapterParserName)
            if not soup:
                logging.error(f'Failed to download tag soup: "{chapterURL}".')
                return None

        return self._InternallyExtractChapter(chapterURL, soup)

    def ExtractMedia(self, URL: str) -> Optional[bytes]:

        ##
        #
        # Extracts binary media (an image, for example).
        #
        # @param URL The URL to be extracted.
        #
        # @return The data extracted, as bytes.
        #
        ##

        if not URL:
            return None

        return self._webSession.Get(URL, text = False, stream = True)

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

        raise NotImplementedError()

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

        raise NotImplementedError()

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

        return URL

    def _GetPrettyStoryURL(self, URL: str) -> Optional[str]:

        ##
        #
        # Returns a "pretty" story URL, i.e. one that can be used for printing in story content.
        #
        # @param URL Input URL (given by the user).
        #
        # @return Pretty URL.
        #
        ##

        return URL