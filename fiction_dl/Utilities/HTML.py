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

from fiction_dl.Concepts.Image import Image

# Standard packages.

from typing import Dict, List, Optional
from urllib.parse import urlparse

# Non-standard packages.

import bleach
from bs4 import BeautifulSoup
from dreamy_utilities.HTML import UnescapeHTMLEntities

#
#
#
# Functions.
#
#
#

def CleanHTML(code: str) -> Optional[str]:

    ##
    #
    # Cleans HTML code.
    #
    # @param code The input code.
    #
    # @return Cleaned input code, or None.
    #
    ##

    if not code:
        return None

    # Unescape entities and remove non-breaking spaces.

    code = UnescapeHTMLEntities(code)
    code = code.replace(u"\u00A0", " ")

    # Return.

    return code

def FindImagesInCode(code: str) -> List[Image]:

    ##
    #
    # Creates a list of Images, based on "img" tags in given code.
    #
    # @param code The input code.
    #
    # @return A List of Image objects, in the same order "img" tags were encountered in the code.
    #
    ##

    soup = BeautifulSoup(code, features = "html.parser")

    return [Image(UnescapeHTMLEntities(tag["src"])) for tag in soup.find_all("img")]

def IsURLAbsolute(URL: str) -> bool:

    ##
    #
    # Checks whether given URL is absolute.
    #
    # @param URL The URL.
    #
    # @return **True** if the URL is absolute, **False** otherwise.
    #
    ##

    if not URL:
        return True

    return bool(urlparse(UnescapeHTMLEntities(URL)).netloc)

def MakeURLAbsolute(URL: str, baseURL: str) -> Optional[str]:

    ##
    #
    # Converts relative URL to absolute URL.
    #
    # @param URL     The input URL.
    # @param baseURL The URL to be prepended in front of the relative input URL.
    #
    # @return Absolute version of the input URL. Optionally None, if something goes wrong.
    #
    ##

    if (not URL) or (not baseURL):
        return None

    elif IsURLAbsolute(URL):
        return URL

    URL = URL if URL.startswith("/") else f"/{URL}"

    return f"{baseURL}{URL}"

def ReformatHTMLToXHTML(code: str) -> Optional[str]:

    ##
    #
    # Reformats given HTML code as valid XHTML.
    #
    # @param code Input HTML code.
    #
    # @return Output XHTML code.
    #
    ##

    if not code:
        return None

    soup = BeautifulSoup(code, "html.parser")
    code = str(soup)

    soup = BeautifulSoup(code, "lxml")
    code = str(soup)

    return code

def StripEmptyTags(
    code: str,
    validEmptyTags: List[str] = [],
    validEmptyTagAttributes: Dict = {}
) -> Optional[str]:

    ##
    #
    # Strips all empty tags from code.
    #
    # @param code                    The input code.
    # @param validEmptyTags          A list of tags allowed to be empty.
    # @param validEmptyTagAttributes A dictionary of attributes with values that allow empty tag to
    #                                get away with being empty.
    #
    # @return The processed code.
    #
    ##

    if not code:
        return None

    soup = BeautifulSoup(code, features = "html.parser")

    tagsStripped = 1

    while tagsStripped:

        tagsStripped = 0

        for tag in soup.find_all(True, recursive = True):

            if tag.name in validEmptyTags:
                continue

            elif tag.find_all(True, recursive = True):
                continue

            elif len(tag.get_text(strip = True)):
                continue

            elif validEmptyTagAttributes:

                validBecauseOfAttributes = False

                for attribute, value in validEmptyTagAttributes.items():

                    if tag.has_attr(attribute) and (value == tag[attribute]):
                        validBecauseOfAttributes = True

                if validBecauseOfAttributes:
                    continue

            tag.decompose()
            tagsStripped += 1

    return str(soup)

def StripHTML(code: str, paragraphSeparator: str = "\n\n") -> Optional[str]:

    ##
    #
    # Converts HTML code to raw text.
    #
    # @param code               The input code.
    # @param paragraphSeparator Text to be inserted in place of paragraph breaks ("</p><p>").
    #
    # @return Raw text generated from the input code.
    #
    ##

    if not code:
        return None

    return BeautifulSoup(
        StripTags(CleanHTML(code), ["p"]),
        "html.parser"
    ).get_text(separator = paragraphSeparator)

def StripTags(code: str, validTags: List[str] = []) -> Optional[str]:

    ##
    #
    # Strips all tags from code, with the exception of those designated "valid" tags.
    #
    # @param code      The input code.
    # @param validTags A List of tags **not** to be stripped from the code.
    #
    # @return The processed code.
    #
    ##

    if not code:
        return None

    return bleach.clean(
        code,
        tags = validTags,
        strip = True
    )