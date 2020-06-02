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
from fiction_dl.Concepts.Story import Story
from fiction_dl.Utilities.Web import GetHostname

# Standard packages.

import requests
from typing import List, Optional

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

    def __init__(self) -> None:

        ##
        #
        # The constructor.
        #
        ##

        self.Story = None

        self._chapterURLs = []

    def GetSupportedHostnames(self) -> List[str]:

        ##
        #
        # Returns a list of hostnames supposed to be supported by the extractor.
        #
        # @return A list of supported hostnames.
        #
        ##

        raise NotImplementedError()

    def SupportsAuthentication(self) -> bool:

        ##
        #
        # Checks whether the extractor supports user authentication.
        #
        # @return **True** if the site *does* support authentication, **False** otherwise.
        #
        ##

        return False

    def Authenticate(self, username: str, password: str) -> bool:

        ##
        #
        # Logs the user in, using provided data.
        #
        # @param username The username.
        # @param password The password.
        #
        # @return **True** if the user has been authenticated correctly, **False** otherwise.
        #
        ##

        return False

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

        self.Story = Story(self._GetNormalizedStoryURL(URL))

        return True

    def Scan(self) -> bool:

        ##
        #
        # Scans the story: generates the list of chapter URLs and retrieves the
        # metadata.
        #
        # @return **False** when the scan fails, **True** when it doesn't fail.
        #
        ##

        raise NotImplementedError()

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

        raise NotImplementedError()

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

        response = requests.get(URL, stream = True)
        if not response.content:
            return None

        return response.content

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

        return URL