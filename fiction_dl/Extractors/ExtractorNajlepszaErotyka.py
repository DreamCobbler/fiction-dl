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
from fiction_dl.Utilities.Text import GetTitleProper

# Standard packages.

import logging
import re
import requests
from typing import List, Optional

# Non-standard packages.

from bs4 import BeautifulSoup
from dreamy_utilities.Text import (
    GetLevenshteinDistance,
    GetLongestLeadingSubstring,
    PrettifyTitle,
    SeparateSubtitle,
    Stringify
)
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
# An extractor dedicated for NajlepszaErotyka.com.pl.
#
##

class ExtractorNajlepszaErotyka(Extractor):

    def __init__(self) -> None:

        ##
        #
        # The constructor.
        #
        ##

        super().__init__()

        self._chapterParserName = "html5lib"

    def GetSupportedHostnames(self) -> List[str]:

        ##
        #
        # Returns a list of hostnames supposed to be supported by the extractor.
        #
        # @return A list of supported hostnames.
        #
        ##

        return [
            "najlepszaerotyka.com.pl",
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

        # Locate relevant elements.

        titleElement = soup.select_one(".container-fluid .row h2")
        if not titleElement:
            logging.error("Title element not found.")
            return False

        titleSpanElement = titleElement.find("span")
        titleSpanElement.replaceWith("")

        metadataElements = soup.select(".container-fluid .row div ul li")
        if not metadataElements:
            logging.error("Author element not found.")
            return False

        authorElement = metadataElements[-1].find("a")
        dateElement = metadataElements[-2]

        # Process metadata.

        authorNameMatch = re.search("/author/(.+)/", authorElement["href"])
        if not authorNameMatch:
            logging.error("Failed to retrieve author's name.")
            return False

        title = self._CleanStoryTitle(titleElement.get_text().strip())
        titleProper = GetTitleProper(title)

        # Find all other chapters of this story.

        self._chapterURLs = []
        chapterTitles = []

        for story in self._FindAllStoriesByAuthor(authorNameMatch.group(1)):

            currentTitleProper = GetTitleProper(story[0])

            distance = GetLevenshteinDistance(currentTitleProper, titleProper)
            if distance > 5:
                continue

            self._chapterURLs.append([story[1], story[2]])
            chapterTitles.append(currentTitleProper)

        datePublished = dateElement.get_text().strip()
        dateUpdated = dateElement.get_text().strip()

        if not self._chapterURLs:

            self._chapterURLs = [self.Story.Metadata.URL]

        else:

            datePublished = self._chapterURLs[0][1]
            dateUpdated = self._chapterURLs[-1][1]

            self._chapterURLs = [x[0] for x in self._chapterURLs]

        # Set the metadata.

        self.Story.Metadata.Title = GetLongestLeadingSubstring(chapterTitles).strip()
        self.Story.Metadata.Author = authorElement.get_text().strip()

        self.Story.Metadata.DatePublished = datePublished
        self.Story.Metadata.DateUpdated = dateUpdated

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

        titleElement = soup.select_one(".container-fluid .row h2")
        if not titleElement:
            logging.error("Title element not found.")
            return False

        if (unwantedElement := titleElement.find("span")):
            unwantedElement.replaceWith("")

        contentElement = soup.select_one(".container .row .entry-content")
        if not contentElement:
            logging.error("Content element not found.")
            return None

        if (unwantedElement := contentElement.select_one("span.rt-reading-time")):
            unwantedElement.replaceWith("")

        if (unwantedElement := contentElement.select_one("div.wpcm-subscribe")):
            unwantedElement.replaceWith("")

        if (unwantedElement := contentElement.select_one("rating-form")):
            unwantedElement.replaceWith("")

        return Chapter(
            title = SeparateSubtitle(self._CleanStoryTitle(titleElement.get_text().strip())),
            content = Stringify(contentElement.encode_contents())
        )

    def _FindAllStoriesByAuthor(self, authorName: str):

        # Download author's page.

        authorsPageURL = f"https://najlepszaerotyka.com.pl/author/{authorName}/"

        soup = self._webSession.GetSoup(authorsPageURL)
        if not soup:
            logging.error("Failed to download page: \"{authorsPageURL\".")
            return None

        # Get the number of subpages.

        pageCount = 1

        paginationElements = soup.select("a.page-numbers")
        if paginationElements:
            pageCount = len(paginationElements)

        # Go over all the pages and collect story links and titles.

        stories = []

        for index in range(1, pageCount + 1):

            pageURL = f"https://najlepszaerotyka.com.pl/author/{authorName}/page/{index}"

            soup = self._webSession.GetSoup(pageURL)
            if not soup:
                logging.error("Failed to download page: \"{pageURL\".")
                return None

            postElements = soup.select("div.post > div.blog-details")

            for element in postElements:

                linkElement = element.select_one("h2 > a")
                if (not linkElement) or (not linkElement.has_attr("href")):
                    continue

                title = ExtractorNajlepszaErotyka._CleanStoryTitle(linkElement.get_text().strip())
                link = linkElement["href"]

                dateElement = element.select_one("li.published")
                date = dateElement.get_text().strip()

                stories.append([title, link, date])

        # Return.

        stories.reverse()
        return stories

    @staticmethod
    def _CleanStoryTitle(title: str) -> str:

        ##
        #
        # Cleans story title (removes recurring elements).
        #
        # @param title The input title.
        #
        # @return The cleaned title.
        #
        ##

        titleMatch = re.search("(.+) \(.+\)", title)
        if not titleMatch:
            return title

        return titleMatch.group(1)