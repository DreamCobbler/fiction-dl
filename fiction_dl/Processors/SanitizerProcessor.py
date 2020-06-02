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

from fiction_dl.Concepts.Processor import Processor
from fiction_dl.Utilities.HTML import CleanHTML, StripEmptyTags, StripTags

# Standard packages.

import re
from typing import Optional

#
#
#
# Classes.
#
#
#

##
#
# Santizes story content, i.e. prepares it to be used by a Formatter.
#
##

class SanitizerProcessor(Processor):

    def Process(self, content: str) -> Optional[str]:

        ##
        #
        # Processes the content given and returns a sanitized version of it.
        #
        # Sanitized code is defined as HTML code that contains no other tags than "p", "img", "hr",
        # "b", "strong", "i", "em" and "u". No tag contains any attributes, no tag is empty.
        #
        # @param content The content to be processed.
        #
        # @return The processed content.
        #
        ##

        if not content:
            return None

        # Fix line breaks.

        content = self._FixLineBreaks(content)

        # Clean the code a bit and make sure it contains only allowed tags.

        content = CleanHTML(content)
        content = StripTags(content, self._Tags)

        # Strip empty tags.

        content = StripEmptyTags(content, ["hr", "img"])

        # Strip newlines.

        Newlines = [
            "\r\n",
            "\r",
            "\n"
        ]

        for newline in Newlines:
            content = content.replace(newline, "")

        # Return processed content.

        return content

    @staticmethod
    def _FixLineBreaks(content: str) -> Optional[str]:

        ##
        #
        # Replaces primitive line breaks ("<br>", "<br/>") with paragraphs.
        #
        # @param content Input content.
        #
        # @return Processed content, optionally **None**.
        #
        ##

        if not content:
            return None

        if ("<br>" in content) or ("<br/>" in content):

            if "<p>" not in content:
                content = "<p>" + content + "</p>"

            content = content.replace("<br>", "</p><p>")
            content = content.replace("<br/>", "</p><p>")

        return content

    _Tags = ["p", "img", "hr", "b", "strong", "i", "em", "u"]