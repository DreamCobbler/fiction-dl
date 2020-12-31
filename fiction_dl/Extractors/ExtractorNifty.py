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
import fiction_dl.Configuration as Configuration

# Standard packages.

from datetime import datetime
import logging
import re
from typing import List, Optional, Tuple

# Non-standard packages.

from bs4 import BeautifulSoup
from dreamy_utilities.Text import PrettifyDate, Stringify
from dreamy_utilities.Web import GetSiteURL

#
#
#
# Classes.
#
#
#

##
#
# An extractor dedicated for Nifty.org.
#
##

class ExtractorNifty(Extractor):

    def __init__(self) -> None:

        ##
        #
        # The constructor.
        #
        ##

        super().__init__()

        self._downloadStorySoupWhenScanning = False
        self._downloadChapterSoupWhenExtracting = False

    def GetSupportedHostnames(self) -> List[str]:

        ##
        #
        # Returns a list of hostnames supposed to be supported by the extractor.
        #
        # @return A list of supported hostnames.
        #
        ##

        return [
            "nifty.org",
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

        # Is it a single chapter story?

        pageCode = self._webSession.Get(URL, textEncoding = "ascii")
        if not pageCode:
            logging.error("Failed to download story page when scanning.")
            return False

        isHTMLCode = (-1 != pageCode.find("<html>"))

        # Process a multi-chapter story.

        if isHTMLCode:

            # Create tag soup.

            soup = self._webSession.GetSoup(URL)

            # Create a list of chapters.

            chapterElements = soup.select("table.table.table-xtra-condensed > tr")
            if not chapterElements:
                logging.error("List of chapters not found.")
                return False

            chapterElements = chapterElements[1:]

            # Process chapters.

            for rowElement in chapterElements:

                cellElements = rowElement.select("td")
                if (not cellElements) or (len(cellElements) < 3):
                    continue

                anchorElement = cellElements[2].select_one("a")
                if (not anchorElement) or (not anchorElement.has_attr("href")):
                    continue

                self._chapterURLs.append(self.Story.Metadata.URL + anchorElement["href"])

            if not self._chapterURLs:
                return False

            self._chapterURLs.reverse()

            # Read the first chapter.

            firstChapterText = self._webSession.Get(self._chapterURLs[0], textEncoding = "ascii")
            if not soup:
                logging.error("Failed to download the first chapter.")
                return False

            firstChapterMetadata = self._ReadChapterMetadata(firstChapterText)
            if not firstChapterMetadata:
                logging.error("Failed to read metadata from the first chapter of the story.")
                return False

            # Read the last chapter.

            lastChapterText = self._webSession.Get(self._chapterURLs[-1], textEncoding = "ascii")
            if not soup:
                logging.error("Failed to download the last chapter.")
                return False

            lastChapterMetadata = self._ReadChapterMetadata(lastChapterText)
            if not lastChapterMetadata:
                logging.error("Failed to read metadata from the last chapter of the story.")
                return False

            # Prepare the metadata.

            title = firstChapterMetadata[0]
            author = firstChapterMetadata[1]
            publicationDate = firstChapterMetadata[2]
            updateDate = lastChapterMetadata[2]

            # Set the metadata.

            self.Story.Metadata.Title = title
            self.Story.Metadata.Author = author

            self.Story.Metadata.DatePublished = publicationDate
            self.Story.Metadata.DateUpdated = updateDate

            self.Story.Metadata.ChapterCount = len(self._chapterURLs)
            self.Story.Metadata.WordCount = 0

            self.Story.Metadata.Summary = "No summary."

        # Process a single-chapter story.

        else:

            # Read chapter metadata.

            chapterMetadata =  self._ReadChapterMetadata(pageCode)
            if not chapterMetadata:
                logging.error("Failed to read metadata from the only chapter of the story.")
                return False

            # Set the metadata.

            self.Story.Metadata.Title = chapterMetadata[0]
            self.Story.Metadata.Author = chapterMetadata[1]

            self.Story.Metadata.DatePublished = chapterMetadata[2]
            self.Story.Metadata.DateUpdated = self.Story.Metadata.DatePublished

            self.Story.Metadata.ChapterCount = 1
            self.Story.Metadata.WordCount = 0

            self.Story.Metadata.Summary = "No summary."

            # Create a list of chapter URLs.

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

        # Read the chapter.

        chapterText = self._webSession.Get(URL, textEncoding = "ascii")
        if not chapterText:
            logging.error("Failed to download a chapter.")
            return False

        chapterText = chapterText.splitlines()
        if len(chapterText) < 4:
            logging.error("Invalid chapter format.")
            return False

        chapterText = chapterText[3:]

        # Format the content.

        chapterCode = ""
        currentParagraphCode = ""

        for line in chapterText:

            if not line:

                chapterCode += f"<p>{currentParagraphCode}</p>"
                currentParagraphCode = ""

            else:

                currentParagraphCode += f" {line.strip()}"

        # Return.

        return Chapter(content = chapterCode)

    @classmethod
    def _ReadChapterMetadata(cls, text: str) -> Optional[Tuple[str, str, str]]:

        ##
        #
        # Reads chapter metadata from its content.
        #
        # @param text Chapter text.
        #
        # @return A tuple consisting of three values: story title, story author, chapter publication
        #         date; optionally **None**.
        #
        ##

        if not text:
            return None

        # Split the chapter text into lines.

        text = text.splitlines()
        if len(text) < 3:
            return None

        # Retrieve lines containing relevant metadata.

        dateString = text[0]
        authorString = text[1]
        titleString = text[2]

        # Retrieve metadata from appropriate lines.

        dateMatch = re.match("Date: (.+)", dateString)
        if not dateMatch:
            return None

        authorMatch = re.match("From: ([^<]+) <", authorString)
        if not authorMatch:
            return None

        titleMatch = re.match("Subject: (.+)", titleString)
        if not titleMatch:
            return None

        # Process and return the metadata.

        date = datetime.strptime(dateMatch.group(1), cls._DATE_FORMAT).strftime("%Y-%m-%d")
        author = authorMatch.group(1).strip()
        title = titleMatch.group(1).strip()

        return (title, author, date)

    # Class constants.

    _DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %z"
