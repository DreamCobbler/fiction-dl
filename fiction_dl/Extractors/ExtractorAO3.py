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
from fiction_dl.Utilities.General import Stringify
from fiction_dl.Utilities.HTML import StripHTML
from fiction_dl.Utilities.Web import DownloadSoup, GetHostname

# Standard packages.

import logging
import re
from typing import List, Optional

# Non-standard packages.

from bs4 import BeautifulSoup

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

        usernameMatch = re.search("/users/([a-zA-Z0-9_]+)", URL)
        if not usernameMatch:
            return None

        username = usernameMatch.group(1)

        normalizedURL = f"https://archiveofourown.org/users/{username}/"
        worksURL = normalizedURL + "works"

        worksSoup = DownloadSoup(worksURL)
        if not worksSoup:
            return None

        worksPagesURLs = []

        if not (worksPaginationElement := worksSoup.find("ol", {"title": "pagination"})):

            worksPagesURLs.append(worksURL)

        else:

            worksPageButtonElements = worksPaginationElement.find_all("li")
            worksPageCount = len(worksPageButtonElements) - 2
            if worksPageCount < 1:
                logging.error("Invalid number of pages on the Works webpage.")
                return None

            for index in range(1, worksPageCount + 1):
                worksPagesURLs.append(worksURL + f"?page={index}")

        workIDs = []

        for pageURL in worksPagesURLs:

            pageSoup = DownloadSoup(pageURL)
            if not pageSoup:
                logging.error("Failed to download a page of the Works webpage.")
                continue

            workElements = pageSoup.find_all("li", {"class": "work"})

            for workElement in workElements:

                linkElement = workElement.find("a")
                if (not linkElement) or (not linkElement.has_attr("href")):
                    logging.error("Failed to retrieve story URL from the Works webpage.")
                    continue

                storyIDMatch = re.search("/works/(\d+)", linkElement["href"])
                if not storyIDMatch:
                    logging.error("Failed to retrieve story ID from its URL.")
                    continue

                storyID = storyIDMatch.group(1)
                workIDs.append(storyID)

        storyURLs = [f"https://archiveofourown.org/works/{ID}" for ID in workIDs]
        return storyURLs

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

        # Extract metadata.

        titleElement = soup.find("h2", {"class": "title"})
        if not titleElement:
            logging.error("Title element not found.")
            return False

        authorElement = soup.find("a", {"rel": "author"})
        # The author might be anonymous, so no error here.

        publishedElement = soup.find("dd", {"class": "published"})
        if not publishedElement:
            logging.error("Date published element not found.")
            return False

        updatedElement = soup.find("dd", {"class": "status"})
        if not updatedElement:
            updatedElement = publishedElement

        chaptersElement = soup.find("dd", {"class": "chapters"})
        if not chaptersElement:
            logging.error("Chapter count element not found.")
            return False

        wordsElement = soup.find("dd", {"class": "words"})
        if not wordsElement:
            logging.error("Word count element not found.")
            return False

        summaryElement = soup.find("blockquote", {"class": "userstuff"})

        # Set the metadata.

        self.Story.Metadata.Title = titleElement.get_text().strip()
        self.Story.Metadata.Author = (
            authorElement.get_text().strip()
            if authorElement else
            "Anonymous"
        )

        self.Story.Metadata.DatePublished = publishedElement.get_text().strip()
        self.Story.Metadata.DateUpdated = updatedElement.get_text().strip()

        self.Story.Metadata.ChapterCount = self._ReadChapterCount(chaptersElement.get_text())
        self.Story.Metadata.WordCount = self._ReadWordCount(wordsElement.get_text())

        self.Story.Metadata.Summary = (
            StripHTML(summaryElement.get_text()).strip()
            if summaryElement else
            "No summary."
        )

        # Extract chapter URLs.

        storyID = self._GetStoryID(self.Story.Metadata.URL)
        if not storyID:
            logging.error("Couldn't retrieve the story's ID.")
            return False

        chapterOptionElements = soup.select("select#selected_id > option")
        self._chapterURLs = [
            self._GetAdultView(f'{self._baseWorkURL}/{storyID}/chapters/{x["value"]}')
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

    def _GetNormalizedStoryURL(self, URL: str) -> Optional[str]:

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

        storyID = self._GetStoryID(URL)

        return self._GetAdultView(f"{ExtractorAO3._baseWorkURL}/{storyID}")

    def _GetAdultView(self, URL: str) -> Optional[str]:

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

    @staticmethod
    def _ReadChapterCount(chaptersDescription: str) -> Optional[int]:

        ##
        #
        # Reads chapter count value from AO3's "chapters" description.
        #
        # @param chaptersDescription Input chapters description.
        #
        # @return Chapter count.
        #
        ##

        if not chaptersDescription:
            return None

        chapterCount = chaptersDescription.strip().split("/")[0]

        try:

            chapterCount = int(chapterCount)

        except ValueError:

            logging.error("Failed to convert chapter count.")

            return None

        return chapterCount

    @staticmethod
    def _ReadWordCount(wordsDescription: str) -> Optional[int]:

        ##
        #
        # Reads word count value from AO3's "words" description.
        #
        # @param wordsDescription Input words description.
        #
        # @return Word count.
        #
        ##

        if not wordsDescription:
            return None

        wordCount = wordsDescription.strip().replace(",", "")

        try:

            wordCount = int(wordCount)

        except ValueError:

            logging.error("Failed to convert word count.")

            return None

        return wordCount

    _baseWorkURL = "https://archiveofourown.org/works"