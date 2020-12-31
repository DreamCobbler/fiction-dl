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
from fiction_dl.Utilities.HTML import StripHTML

# Standard packages.

from datetime import datetime
import logging
from math import ceil
import re
from typing import List, Optional

# Non-standard packages.

from bs4 import BeautifulSoup
from dreamy_utilities.Text import Stringify
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
# An extractor dedicated for hentai-foundry.com.
#
##

class ExtractorHentaiFoundry(Extractor):

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
            "hentai-foundry.com"
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

        usernameStoryIDMatch = re.search("/user/([a-zA-Z0-9_]+)/(\d+)", URL)
        if usernameStoryIDMatch:
            return None

        usernameMatch = re.search("/user/([a-zA-Z0-9_]+)", URL)
        if not usernameMatch:
            return None

        username = usernameMatch.group(1)
        normalizedURL = f"http://www.hentai-foundry.com/stories/user/{username}/"

        pageSoup = self._webSession.GetSoup(self._GetAdultView(normalizedURL))
        if not pageSoup:
            return None

        pageCountDescriptionElement = pageSoup.select_one(".galleryHeader > .summary")
        pageCountDescription = pageCountDescriptionElement.get_text().strip()

        pageCountDescriptionMatch = re.search(
            "Displaying (\d+)-(\d+) of (\d+) results",
            pageCountDescription
        )

        if not pageCountDescriptionMatch:
            logging.error("Failed to retrieve page count of the Stories tab.")
            return None

        storiesPerPage = int(pageCountDescriptionMatch.group(2))
        storiesInTotal = int(pageCountDescriptionMatch.group(3))

        if not storiesPerPage:
            return None

        pageCount = ceil(storiesInTotal / storiesPerPage)

        storyURLs = []
        for pageIndex in range(1, pageCount + 1):

            pageURL = self._GetAdultView(
                f"http://www.hentai-foundry.com/stories/user/{username}?page={pageIndex}"
            )

            pageSoup = self._webSession.GetSoup(pageURL)
            if not pageSoup:
                return None

            storyLinkElements = pageSoup.select(".items > .storyRow > .titlebar > a")

            for linkElement in storyLinkElements:

                if not linkElement.has_attr("href"):
                    continue

                storyURLs.append(self._baseURL + linkElement["href"])

        return storyURLs

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

        # Locate metadata.

        titleElement = soup.select_one(".titlebar a")
        if not titleElement:
            logging.error("Title element not found.")
            return False

        authorElement = soup.select_one(".storyInfo > .col1 > a")
        if not authorElement:
            logging.error("Author element not found.")
            return False

        datesElements = soup.select(".storyInfo > .col2 > .indent")
        if (not datesElements) or (len(datesElements) < 2):
            logging.error("Dates elements not found.")
            return False

        datePublishedElement = datesElements[0]
        dateUpdatedElement = datesElements[1]

        summaryElement = soup.select_one(".storyDescript")
        if not summaryElement:
            logging.error("Summary element not found.")
            return False

        chapterCountWordCountElement = soup.select_one(".storyInfo > .col3")
        if not chapterCountWordCountElement:
            logging.error("Chapter/word count elements not found.")
            return False

        # Extract and save metadata.

        self.Story.Metadata.Title = titleElement.get_text().strip()
        self.Story.Metadata.Author = authorElement.get_text().strip()

        rawDatePublished = datePublishedElement.get_text().strip()
        rawDateUpdated = dateUpdatedElement.get_text().strip()

        self.Story.Metadata.DatePublished = self._ReformatDate(rawDatePublished)
        self.Story.Metadata.DateUpdated = self._ReformatDate(rawDateUpdated)

        chapterCountWordCountDescription = StripHTML(
            chapterCountWordCountElement.get_text().strip()
        )
        chapterCountMatch = re.search("Chapters:\s+(\d+)", chapterCountWordCountDescription)
        if not chapterCountMatch:
            logging.error("Chapter count not found.")
            return False

        wordCountMatch = re.search("Words:\s+([0-9,]+)", chapterCountWordCountDescription)
        if not wordCountMatch:
            logging.error("Word count not found.")
            return False

        self.Story.Metadata.ChapterCount = int(chapterCountMatch.group(1))
        self.Story.Metadata.WordCount = self._ReadWordCount(wordCountMatch.group(1))

        self.Story.Metadata.Summary = StripHTML(summaryElement.get_text().strip())

        # Retrieve chapter URLs.

        chapterLinkElements = soup.select(".boxbody > p > a")
        if not chapterLinkElements:
            logging.error("No chapter links found.")
            return False

        for linkElement in chapterLinkElements:

            if not linkElement.has_attr("href"):
                continue

            self._chapterURLs.append(self._baseURL + linkElement["href"])

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

        if (titleElement := soup.select_one("#viewChapter > .boxheader")):

            chapterTitle = titleElement.get_text().strip()

        # Read the content.

        storyTextElement = soup.select_one("#viewChapter > .boxbody")
        if not storyTextElement:
            logging.error("Story text element not found.")
            return None

        return Chapter(
            title = chapterTitle,
            content = Stringify(storyTextElement.encode_contents())
        )

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

        return self._GetAdultView(URL)

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

        return URL + "?enterAgree=1&size=0"

    @staticmethod
    def _ReformatDate(date: str) -> Optional[str]:

        if not date:
            return None

        try:

            date = datetime.strptime(date, "%B %d, %Y").strftime("%Y-%m-%d")

            return date

        except ValueError:

            return GetCurrentDate()

    @staticmethod
    def _ReadWordCount(wordsDescription: str) -> Optional[int]:

        ##
        #
        # Reads word count value from HF's "words" description.
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

    _baseURL = "http://www.hentai-foundry.com"