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

# Standard packages.

import logging
import requests
from typing import List, Optional

# Non-standard packages.

from bs4 import BeautifulSoup
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
# An extractor dedicated for www.asstr.org/~Kristen/.
#
##

class ExtractorAsstrKristen(Extractor):

    def __init__(self) -> None:

        ##
        #
        # The constructor.
        #
        ##

        super().__init__()

        self._downloadStorySoupWhenScanning = False
        self._downloadChapterSoupWhenExtracting = False

        self._storyText = None

    def GetSupportedHostnames(self) -> List[str]:

        ##
        #
        # Returns a list of hostnames supposed to be supported by the extractor.
        #
        # @return A list of supported hostnames.
        #
        ##

        return [
            "asstr.org",
        ]

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

        # Download the story.

        self._storyText = requests.get(URL).content.decode(encoding = "ascii", errors = "ignore")
        if not self._storyText:
            logging.error("Failed to download story page when scanning.")
            return False

        # Locate and read the metadata.

        title = None
        author = None
        summary = None

        storyLines = self._storyText.split("\n")
        storyLines = [x for x in storyLines if x.strip()]

        firstSeparatorLineIndex = -1
        secondSeparatorLineIndex = -1

        for index, line in enumerate(storyLines):

            if (-1 != firstSeparatorLineIndex) and (-1 != secondSeparatorLineIndex):
                break

            elif not line.strip().startswith("***"):
                continue

            elif -1 == firstSeparatorLineIndex:
                firstSeparatorLineIndex = index

            elif -1 == secondSeparatorLineIndex:
                secondSeparatorLineIndex = index

        if (-1 == firstSeparatorLineIndex) or (-1 == secondSeparatorLineIndex):
            logging.error("Failed to locate the metadata.")
            return False

        author = storyLines[firstSeparatorLineIndex - 1][3:]
        if (separatorPosition := author.find("(")) and (-1 != separatorPosition):
            author = author[:separatorPosition].strip()
        if not author:
            logging.error("Failed to read story author.")
            return False

        title = storyLines[firstSeparatorLineIndex - 2]
        if not title:
            logging.error("Failed to read story title.")
            return False

        summary = " ".join(storyLines[firstSeparatorLineIndex + 1:secondSeparatorLineIndex]).strip()

        # Set the metadata.

        self.Story.Metadata.Title = title
        self.Story.Metadata.Author = author

        self.Story.Metadata.DatePublished = "?"
        self.Story.Metadata.DateUpdated = "?"

        self.Story.Metadata.ChapterCount = 1
        self.Story.Metadata.WordCount = 0

        self.Story.Metadata.Summary = summary

        # Set chapter URLs.

        self._chapterURLs = [URL]

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

        # Define usual story endings.

        USUAL_ENDINGS = [
            "~~~",
            "~ ~ ~ ",
            "the end",
            "end",
        ]

        # Locate and cut the end.

        text = self._storyText.splitlines()

        separatorLineIndices = []
        endLineIndices = []

        for index, line in enumerate(text):

            strippedLine = line.strip()

            if strippedLine.startswith("***") or strippedLine.startswith("------"):
                separatorLineIndices.append(index)

            lowercaseLine = strippedLine.lower()

            for ending in USUAL_ENDINGS:
                if lowercaseLine.startswith(ending):
                    endLineIndices.append(index)
                    continue

        firstLineIndex = separatorLineIndices[1] if separatorLineIndices else -1
        lastLineIndex = endLineIndices[-1] if endLineIndices else -1

        if -1 == firstLineIndex:
            logging.error("Invalid story content format.")
            return None

        if -1 == lastLineIndex:
            text = text[firstLineIndex + 1:]
        else:
            text = text[firstLineIndex + 1:lastLineIndex]

        # Format the content.

        chapterCode = ""
        currentParagraphCode = ""

        for line in text:

            if not line:

                chapterCode += f"<p>{currentParagraphCode}</p>"
                currentParagraphCode = ""

            else:

                currentParagraphCode += f" {line.strip()}"

        # Return.

        return Chapter(content = chapterCode)
