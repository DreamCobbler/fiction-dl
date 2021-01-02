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

from __future__ import annotations

# Application.

from fiction_dl.Processors.TypographyProcessor import TypographyProcessor

# Standard packages.

from copy import deepcopy
from typing import List, Optional

# Non-standard packages.

from dreamy_utilities.HTML import EscapeHTMLEntities, UnescapeHTMLEntities
from dreamy_utilities.Text import PrettifyDate, PrettifyNumber, PrettifyTitle, Truncate

#
#
#
# Classes.
#
#
#

##
#
# Represents a story's metadata.
#
##

class Metadata:

    def __init__(self, prettifyTitle: bool = True) -> None:

        ##
        #
        # The constructor.
        #
        # @param prettifyTitle Should the title be prettified when returning prettified metadata?
        #
        ##

        # Initialize member variables.

        self.URL = None

        self.Title = None
        self.Author = None
        self.Summary = None

        # All dates are ISO 8601 dates (YYYY-MM-DD).
        self.DatePublished = None
        self.DateUpdated = None
        self.DateExtracted = None

        self.ChapterCount = None
        self.WordCount = None

        # Save the options.

        self._prettifyTitle = prettifyTitle

    def AreValuesMissing(self) -> List[str]:

        ##
        #
        # Checks whether the object contains all the information it's meant to contain.
        #
        # @return A list of missing values.
        #
        ##

        missingValues = []

        if not self.URL:
            missingValues.append("URL")

        if not self.Title:
            missingValues.append("Title")

        if not self.Author:
            missingValues.append("Author")

        if not self.DatePublished:
            missingValues.append("DatePublished")

        if not self.DateUpdated:
            missingValues.append("DateUpdated")

        if not self.DateExtracted:
            missingValues.append("DateExtracted")

        if not self.ChapterCount:
            missingValues.append("ChapterCount")

        return missingValues

    def GetPrettified(self, escapeHTMLEntities: bool = False) -> Metadata:

        ##
        #
        # Returns prettified metadata (to be used when printing anything).
        #
        # @return Prettified metadata.
        #
        ##

        metadata = deepcopy(self)
        metadata.Process(summaryLength = None)

        metadata.DatePublished = PrettifyDate(self.DatePublished)
        metadata.DateUpdated = PrettifyDate(self.DateUpdated)
        metadata.DateExtracted = PrettifyDate(self.DateExtracted)

        metadata.ChapterCount = PrettifyNumber(self.ChapterCount)
        metadata.WordCount = PrettifyNumber(self.WordCount)

        if escapeHTMLEntities:

            metadata.URL = EscapeHTMLEntities(metadata.URL)
            metadata.Title = EscapeHTMLEntities(metadata.Title)
            metadata.Author = EscapeHTMLEntities(metadata.Author)
            metadata.Summary = EscapeHTMLEntities(metadata.Summary)

            metadata.DatePublished = EscapeHTMLEntities(metadata.DatePublished)
            metadata.DateUpdated = EscapeHTMLEntities(metadata.DateUpdated)
            metadata.DateExtracted = EscapeHTMLEntities(metadata.DateExtracted)

            metadata.ChapterCount = EscapeHTMLEntities(metadata.ChapterCount)
            metadata.WordCount = EscapeHTMLEntities(metadata.WordCount)

        return metadata

    def Process(self, summaryLength: Optional[int] = 250) -> None:

        ##
        #
        # Processes the metadata. To be used before generating output files.
        #
        ##

        prettifiedTitle = PrettifyTitle(self.Title, removeContext = True) if self._prettifyTitle else self.Title

        typographyProcessor = TypographyProcessor()

        self.Title = typographyProcessor.Process(prettifiedTitle).strip()
        self.Title = UnescapeHTMLEntities(self.Title)

        self.Summary = typographyProcessor.Process(self.Summary).strip()
        self.Summary = UnescapeHTMLEntities(self.Summary)

        if summaryLength:
            self.Summary = Truncate(self.Summary, summaryLength)

    def __bool__(self) -> bool:

        ##
        #
        # The bool operator.
        #
        # @return **True** if the metadata exists.
        #
        ##

        return bool(self.Title)