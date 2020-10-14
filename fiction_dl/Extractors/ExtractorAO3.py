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
import re
from typing import List, Optional

# Non-standard packages.

from bs4 import BeautifulSoup
from dreamy_utilities.HTML import ReadElementText
from dreamy_utilities.Text import DeprettifyAmount, DeprettifyNumber, Stringify
from dreamy_utilities.Web import DownloadSoup, GetHostname

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

        # Extract metadata.

        try:

            title = ReadElementText(soup, "h2.title")
            if not title:
                raise RuntimeError("title.")

            author = ReadElementText(soup, "a[rel~=author]")
            # Author is optional.

            datePublished = ReadElementText(soup, "dd.published")
            if not datePublished:
                raise RuntimeError("date of publication.")

            dateUpdated = ReadElementText(soup, "dd.published")
            if not dateUpdated:
                raise RuntimeError("date of most recent update.")

            chapterAmount = ReadElementText(soup, "dd.chapters")
            if not chapterAmount:
                raise RuntimeError("chapter count.")

            wordCount = ReadElementText(soup, "dd.words")
            if not wordCount:
                raise RuntimeError("word count.")

            summary = ReadElementText(soup, "blockquote.userstuff")
            # Summary is optional.

        except RuntimeError as exception:

            logging.error("Failed to read metadata: {exception}.")

            return False

        # Set the metadata.

        self.Story.Metadata.Title = title
        self.Story.Metadata.Author = author or "Anonymous"

        self.Story.Metadata.DatePublished = datePublished
        self.Story.Metadata.DateUpdated = dateUpdated

        self.Story.Metadata.ChapterCount = DeprettifyAmount(chapterAmount)[0]
        self.Story.Metadata.WordCount = DeprettifyNumber(wordCount)

        self.Story.Metadata.Summary = summary or "No summary."

        # Extract chapter URLs.

        storyID = self._GetStoryID(self.Story.Metadata.URL)
        if not storyID:
            logging.error("Couldn't retrieve the story's ID.")
            return False

        chapterOptionElements = soup.select("select#selected_id > option")
        self._chapterURLs = [
            self._GetAdultView(f'{self._BASE_WORK_URL}/{storyID}/chapters/{x["value"]}')
            for x in chapterOptionElements
            if x.has_attr("value")
        ]

        if not self._chapterURLs:
            self._chapterURLs = [self.Story.Metadata.URL]

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

        chapterTitle = None

        if (titleElement := soup.select_one("h3.title")):

            if (chapterTitleMatch := re.search("^.* \d+: (.*)", titleElement.get_text().strip())):
                chapterTitle = chapterTitleMatch.group(1)

        # Read the content.

        storyTextElement = soup.select_one("div.userstuff")
        if not storyTextElement:
            logging.error("Story text element not found.")
            return None

        if (landmarkElement := storyTextElement.select_one("h3#work")):
            landmarkElement.decompose()

        return Chapter(
            title = chapterTitle,
            content = Stringify(storyTextElement.encode_contents())
        )

    @staticmethod
    def _ScanWorks(URL: str) -> Optional[List[str]]:

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

        soup = DownloadSoup(URL)
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

            soup = DownloadSoup(pageURL)
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

        return ExtractorAO3._GetAdultView(
            f"{ExtractorAO3._BASE_WORK_URL}/{ExtractorAO3._GetStoryID(URL)}"
        )

    @staticmethod
    def _GetAdultView(URL: str) -> Optional[str]:

        ##
        #
        # Returns a URL with option allowing to view adult content set.
        #
        # @param URL Input URL.
        #
        # @return Adult content proofed URL.
        #
        ##

        if not URL:
            return None

        return URL + "?view_adult=true"

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

    _BASE_WORK_URL = "https://archiveofourown.org/works"
    _BASE_USER_URL = "https://archiveofourown.org/users"
    _BASE_SERIES_URL = "https://archiveofourown.org/series"
    _BASE_COLLECTION_URL = "https://archiveofourown.org/collections"