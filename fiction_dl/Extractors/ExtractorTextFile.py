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

import requests
from typing import List, Optional

#
#
#
# Classes.
#
#
#

class ExtractorTextFile(Extractor):

    def __init__(self) -> None:

        ##
        #
        # The constructor.
        #
        ##

        super().__init__()

        self._filePath = None
        self._fileContent = None

    def GetSupportedHostnames(self) -> List[str]:

        ##
        #
        # Returns a list of hostnames supposed to be supported by the extractor.
        #
        # @return A list of supported hostnames.
        #
        ##

        return []

    def Initialize(self, filePath: str) -> bool:

        ##
        #
        # Initializes the extractor with given URL.
        #
        # @param filePath The URL in question.
        #
        # @return **True** if the extractor can handle the URL, **False** otherwise.
        #
        ##

        self._filePath = filePath
        self.Story = Story()

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

        if not self._filePath:
            return False

        try:

            with open(self._filePath, "r", encoding = "utf-8") as file:
                self._fileContent = file.readlines()

        except OSError:

            return False

        if len(self._fileContent) < 6:
            return False

        self.Story.Metadata.URL = self._fileContent[1].strip()

        self.Story.Metadata.Title = self._fileContent[2].strip()
        self.Story.Metadata.Author = self._fileContent[3].strip()

        self.Story.Metadata.Summary = self._fileContent[4].strip()

        self.Story.Metadata.ChapterCount = 1
        self.Story.Metadata.WordCount = 0

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

        if 1 != index:
            return None

        chapterContent = "".join(self._fileContent[4:])

        return Chapter(content = chapterContent)