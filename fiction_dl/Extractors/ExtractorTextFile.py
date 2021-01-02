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
import fiction_dl.Configuration as Configuration

# Standard packages.

from itertools import groupby
from typing import List, Optional

# Non-standard packages.

from dreamy_utilities.Filesystem import ReadTextFile

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
        self._chapters = None

    def RequiresBreaksBetweenRequests(self) -> bool:

        ##
        #
        # Does the extractor require the application to sleep between subsequent reqests?
        #
        # @return **True** if it does, **False** otherwise.
        #
        ##

        return False

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

        if not ReadTextFile(filePath, lines = True):
            return False

        self._filePath = filePath
        self.Story = Story()

        return True

    def ScanChannel(self, URL: str) -> Optional[List[str]]:

        ##
        #
        # Scans the channel: generates the list of story URLs.
        #
        # @return **None** when the scan fails, a list of story URLs when it doesn't fail.
        #
        ##

        lines = ReadTextFile(self._filePath, lines = True)
        if (not lines) or lines[0].startswith(Configuration.TextSourceFileMagicText):
            return None

        return self._ReadURLsFromLines(lines)

    def ScanStory(self) -> bool:

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

        # Read the file.

        self._fileContent = ReadTextFile(self._filePath, lines = True)
        if (not self._fileContent) or len(self._fileContent) < 6:
            return False

        # Calculate chapter count.

        chapterCount = 1

        for line in self._fileContent:
            if line.startswith(Configuration.TextSourceFileChapterBreak):
                chapterCount += 1

        # Set the metadata.

        self.Story.Metadata.URL = self._fileContent[1].strip()
        self.Story.Metadata.Title = self._fileContent[2].strip()
        self.Story.Metadata.Author = self._fileContent[3].strip()
        self.Story.Metadata.Summary = self._fileContent[4].strip()
        self.Story.Metadata.ChapterCount = chapterCount
        self.Story.Metadata.WordCount = 0

        # Format chapter content.

        chapterGroups = groupby(
            self._fileContent[5:],
            lambda x: x.startswith(Configuration.TextSourceFileChapterBreak)
        )

        self._chapters = [list(group) for x, group in chapterGroups if not x]

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

        if (not self._chapters) or (index < 1):
            return None

        return Chapter(content = "".join(self._chapters[index - 1]))

    @staticmethod
    def _ReadURLsFromLines(lines: List[str]) -> List[str]:

        ##
        #
        # Creates a list of input URLs from lines of a text file.
        #
        # @param lines List of strings being read lines of a text file.
        #
        # @return List of strings: URLs of the stories to be downloaded.
        #
        ##

        if not lines:
            return lines

        URLs = [x.strip() for x in lines]
        URLs = [x for x in URLs if len(x)] # Ignore empty lines.
        URLs = [x for x in URLs if not x.startswith("#")] # Ignore comments.

        return URLs