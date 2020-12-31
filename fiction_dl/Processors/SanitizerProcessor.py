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
from fiction_dl.Utilities.HTML import CleanHTML, StripEmptyTags, StripTags

# Standard packages.

import re
from typing import Optional

# Non-standard packages.

from bs4 import  BeautifulSoup

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
        # "b", "strong", "i", "em", "u", and "a". No tag is empty, other than "img" and "hr". No tag
        # containes any attributes, with the exception of "a" - and the only attribute this tag is
        # allowed to have is "href".
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

        # Strip attributes.

        soup = BeautifulSoup(content, features = "html.parser")

        for tag in soup.find_all(lambda x: len(x.attrs) > 0):

            for name, value in list(tag.attrs.items()):

                if ("a" == tag.name) and ("href" == name):

                    # Fix parentheses - Typography Processor messes the up.

                    if value.startswith("“"):
                        value = value[1:]

                    if value.endswith("”"):
                        value = value[:-1]

                    tag[name] = value

                    continue

                else:

                    del tag[name]

        content = str(soup)

        # Strip newlines.

        Newlines = [
            "\r\n",
            "\r",
            "\n"
        ]

        for newline in Newlines:
            content = content.replace(newline, " ")

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

    _Tags = ["p", "img", "hr", "b", "strong", "i", "em", "u", "a"]