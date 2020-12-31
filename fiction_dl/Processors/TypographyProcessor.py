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

from fiction_dl.Concepts.Processor import Processor

# Standard packages.

import re
from typing import Optional

# Non-standard packages.

from bs4 import BeautifulSoup

#
#
#
# Classes.
#
#
#

##
#
# Clears/fixes the typography.
#
##

class TypographyProcessor(Processor):

    def Process(self, content: str) -> Optional[str]:

        ##
        #
        # Processes the content given and returns a modified version of it.
        #
        # @param content The content to be processed.
        #
        # @return The processed content.
        #
        ##

        if not content:
            return None

        content = self._FixQuotationMarks(content)
        if content is None:
            return None

        content = self._FixPrimitivePunctuation(content)
        if content is None:
            return None

        content = self._FixPunctuationWhitespace(content)
        if content is None:
            return None

        content = self._FixParagraphWhitespace(content)
        if content is None:
            return None

        content = self._ReplacePseudolinesWithLines(content)
        if content is None:
            return None

        return content

    @staticmethod
    def _FixQuotationMarks(content: str) -> Optional[str]:

        ##
        #
        # Replaces quotation marks with prettier ones.
        #
        # @param content Input content.
        #
        # @return Processed content, optionally **None**.
        #
        ##

        if not content:
            return None

        quotationMarkCount = 0;
        processedContent = ""

        for letter in content:

            if '"' != letter:

                processedContent += letter

            else:

                quotationMarkCount += 1

                processedContent += "“" if (quotationMarkCount % 2) else "”"

        return processedContent

    @staticmethod
    def _FixPrimitivePunctuation(content: str) -> Optional[str]:

        ##
        #
        # Fixes "primitive" whitespace. That is, it replaces things like "..." with things like
        # "…".
        #
        # @param content Input content.
        #
        # @return Processed content, optionally **None**.
        #
        ##

        if not content:
            return None

        # Example: ".." -> "…"
        content = re.sub("(\.){2,}", "…", content)

        # Example: ". . ." -> "…"
        content = re.sub("(\.\\s){2,}", "…", content)

        # Example: "………" -> "…"
        content = re.sub("…+", "…", content)

        # Example: "…." -> "…"
        content = re.sub("…\.+", "…", content)

        # Example: "???" -> "?"
        content = re.sub("\?+", "?", content)

        # Example: " - " -> " — "
        content = re.sub("(\\s)-(\\s)", r"\1—\2", content)

        # Example: "-----" -> "—"
        content = re.sub("(\-){2,}", "—", content)

        return content

    @staticmethod
    def _FixPunctuationWhitespace(content: str) -> Optional[str]:

        ##
        #
        # Fixes whitespace around punctuation.
        #
        # @param content Input content.
        #
        # @return Processed content, optionally **None**.
        #
        ##

        if not content:
            return None

        # Example: "  " -> " "
        content = re.sub("(\\s){2,}", " ", content)

        # Example: "A , B" -> "A, B"
        content = re.sub("(\\s),(\\s)", r",\2", content)

        # Example: "A ,B" -> "A, B"
        content = re.sub("(\\s),(\\S)", r", \2", content)

        # Example: "A…B" -> "A… B"
        content = re.sub("(\\S)…(\\S)", r"\1… \2", content)

        # Example: "A … B" -> "A… B"
        content = re.sub("(\\s)…(\\s)", r"…\2", content)

        # Example: " ?" -> "?"
        content = re.sub("(\\s)\\?", "?", content)

        # Example: " !" -> "!"
        content = re.sub("(\\s)\\!", "!", content)

        # Example: "???" -> "?"
        content = re.sub("\?+", "?", content)

        # Example: "A- " -> "A— "
        content = re.sub("(\\S)-(\\s)", r"\1—\2", content)

        # Example: " -A" -> " — A"
        content = re.sub("(\\s)-(\\S)", r" — \2", content)

        # Example: "A—B" -> "A — B"
        content = re.sub("(\\S)—(\\S)", r"\1 — \2", content)

        return content

    @staticmethod
    def _FixParagraphWhitespace(content: str) -> Optional[str]:

        ##
        #
        # Strips preceding and trailing whitespace from paragraph tags.
        #
        # @param content Input content.
        #
        # @return Processed content, optionally **None**.
        #
        ##

        if not content:
            return None

        content = re.sub(r"<p>\s*(.*)\s*</p>", r"<p>\1</p>", content)

        return content

    @staticmethod
    def _ReplacePseudolinesWithLines(content: str) -> Optional[str]:

        ##
        #
        # Replaces pseudolines (i.e. things like "*************" or "----") with proper horizontal
        # lines.
        #
        # @param content Input content.
        #
        # @return Processed content, optionally **None**.
        #
        ##

        if not content:
            return None

        # Replace pseudolines stretching entire paragraphs.

        soup = BeautifulSoup(content, features = "html.parser")

        MAXIMUM_PSEUDOLINE_LENGTH = 30
        for tag in soup.find_all(recursive = True):

            if "p" != tag.name:
                continue

            tagText = tag.get_text()

            if len(tagText) > MAXIMUM_PSEUDOLINE_LENGTH:
                continue

            elif not any(x.isalnum() for x in tagText):
                tag.replace_with(soup.new_tag("hr"))

        content = str(soup)

        # Replace inline pseudolines.

        Pseudolines = [

            "(o\-){3,}",
            "(o \-){3,}",

            "(\*){3,}",
            "(\* ){2,}",

            "(\-){3,}",
            "(\- ){3,}",

            "(\-[a-zA-Z]){3,}",
            "(\- [a-zA-Z]){3,}",

            "(\—){3,}",
            "(\— ){3,}",

            "(\—[a-zA-Z]){3,}",
            "(\— [a-zA-Z]){3,}",

            "(\+){3,}",
            "(\+ ){2,}",

            "(\_){3,}",
            "(\_ ){2,}",

        ]

        for pseudoline in Pseudolines:
            content = re.sub(pseudoline, "<hr/>", content)

        # Remove multiple lines in sequence.

        soup = BeautifulSoup(content, features = "html.parser")

        for tag in soup.find_all(recursive = True):

            if "hr" != tag.name:
                continue

            elif not tag.next_sibling:
                continue

            elif "hr" != tag.next_sibling.name:
                continue

            tag.decompose()

        content = str(soup)

        # Return.

        return content