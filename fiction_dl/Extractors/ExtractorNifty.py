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

from datetime import datetime
import logging
import re
import requests
from typing import List, Optional

# Non-standard packages.

from bs4 import BeautifulSoup
from dreamy_utilities.Text import PrettifyDate, Stringify
from dreamy_utilities.Web import DownloadPage, DownloadSoup, GetSiteURL

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

        firstChapterText = str(requests.get(self._chapterURLs[0]).content.decode("ansi"))
        if not soup:
            logging.error("Failed to download the first chapter.")
            return False

        firstChapterText = firstChapterText.splitlines()
        if len(firstChapterText) < 3:
            logging.error("The first chapter doesn't contain metadata.")
            return False

        firstChapterDateString = firstChapterText[0]
        firstChapterAuthorString = firstChapterText[1]
        firstChapterTitleString = firstChapterText[2]

        # Read the last chapter.

        lastChapterText = str(requests.get(self._chapterURLs[-1]).content.decode("ansi"))
        if not soup:
            logging.error("Failed to download the last chapter.")
            return False

        lastChapterText = lastChapterText.splitlines()
        if len(lastChapterText) < 1:
            logging.error("The last chapter doesn't contain metadata.")
            return False

        lastChapterDateString = lastChapterText[0]

        # Process read metadata strings.

        firstChapterDateMatch = re.match("Date: (.+)", firstChapterDateString)
        if not firstChapterDateMatch:
            logging.error("Couldn't read the first date from chapter metadata.")
            return False

        authorMatch = re.match("From: ([^<]+) <", firstChapterAuthorString)
        if not authorMatch:
            logging.error("Couldn't read the author from chapter metadata.")
            return False

        titleMatch = re.match("Subject: (.+)", firstChapterTitleString)
        if not titleMatch:
            logging.error("Couldn't read the title from chapter metadata.")
            return False

        lastChapterDateMatch = re.match("Date: (.+)", lastChapterDateString)
        if not lastChapterDateMatch:
            logging.error("Couldn't read the last date from chapter metadata.")
            return False

        # Set the metadata.

        self.Story.Metadata.Title = titleMatch.group(1).strip()
        self.Story.Metadata.Author = authorMatch.group(1).strip()

        self.Story.Metadata.DatePublished = datetime.strptime(
            firstChapterDateMatch.group(1).strip(),
            "%a, %d %b %Y %H:%M:%S %z"
        ).strftime("%Y-%m-%d")
        self.Story.Metadata.DateUpdated = datetime.strptime(
            lastChapterDateMatch.group(1).strip(),
            "%a, %d %b %Y %H:%M:%S %z"
        ).strftime("%Y-%m-%d")

        self.Story.Metadata.ChapterCount = len(self._chapterURLs)
        self.Story.Metadata.WordCount = 0

        self.Story.Metadata.Summary = "No summary."

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

        chapterText = str(requests.get(URL).content.decode("ansi"))
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