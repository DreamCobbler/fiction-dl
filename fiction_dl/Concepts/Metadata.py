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

from __future__ import annotations

# Application.

from fiction_dl.Processors.TypographyProcessor import TypographyProcessor
from fiction_dl.Utilities.HTML import Unescape
from fiction_dl.Utilities.Text import GetTitleProper, PrettifyDate, PrettifyNumber, Truncate

# Standard packages.

from copy import deepcopy
import html
from typing import Optional

# Non-standard packages.

from titlecase import titlecase

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

    def __init__(self) -> None:

        ##
        #
        # The constructor.
        #
        ##

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

            metadata.Title = html.escape(metadata.Title)
            metadata.Author = html.escape(metadata.Author)
            metadata.Summary = html.escape(metadata.Summary)

            metadata.DatePublished = html.escape(metadata.DatePublished)
            metadata.DateUpdated = html.escape(metadata.DateUpdated)
            metadata.DateExtracted = html.escape(metadata.DateExtracted)

            metadata.ChapterCount = html.escape(metadata.ChapterCount)
            metadata.WordCount = html.escape(metadata.WordCount)

        return metadata

    def Process(self, summaryLength: Optional[int] = 250) -> None:

        ##
        #
        # Processes the metadata. To be used before generating output files.
        #
        ##

        typographyProcessor = TypographyProcessor()

        self.Title = titlecase(typographyProcessor.Process(GetTitleProper(self.Title)).strip())
        self.Title = Unescape(self.Title)

        self.Summary = typographyProcessor.Process(self.Summary).strip()

        if summaryLength:
            self.Summary = Truncate(self.Summary, summaryLength)