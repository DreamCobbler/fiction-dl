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

from fiction_dl.Utilities.General import Stringify
from fiction_dl.Utilities.HTML import Unescape

# Standard packages.

from datetime import datetime
import re
from typing import Any, Optional

# Non-standard packages.

from babel.dates import format_date
from babel.numbers import format_number
import numpy
import pykakasi
from titlecase import titlecase

#
#
#
# Functions.
#
#
#

def FillTemplate(values: Any, template: str) -> str:

    ##
    #
    # Fills in a template using values coming from an object/a namespace/anything that responds to
    # "vars()". Variables in the template need to written like that: "@@@variable_name@@@".
    #
    # @param values   Iterable values.
    # @param template Template code.
    #
    # @return Template code with variables filled in.
    #
    ##

    availableValues = [x for x in vars(values) if not x.startswith("_")]

    for value in availableValues:
        template = template.replace(f"@@@{value}@@@", Stringify(getattr(values, value)))

    return template

def GetLevenshteinDistance(firstString: str, secondString: str) -> int:

    ##
    #
    # Calculates the Levenshtein distance between a pair of strings.
    #
    # @param firstString  The first string.
    # @param secondString The second string.
    #
    # @return The distance between the two strings.
    #
    ##

    if (not firstString) or (not secondString):
        return 0

    sizeH = len(firstString) + 1
    sizeV = len(secondString) + 1

    matrix = numpy.zeros((sizeH, sizeV))
    for x in range(sizeH):
        matrix[x, 0] = x
    for y in range(sizeV):
        matrix[0, y] = y

    for x in range(1, sizeH):

        for y in range(1, sizeV):

            if firstString[x - 1] == secondString[y - 1]:

                matrix[x, y] = min(
                    matrix[x - 1, y    ] + 1,
                    matrix[x - 1, y - 1]    ,
                    matrix[x    , y - 1] + 1
                )

            else:

                matrix[x, y] = min(
                    matrix[x - 1, y    ] + 1,
                    matrix[x - 1, y - 1] + 1,
                    matrix[x    , y - 1] + 1
                )

    return matrix[sizeH - 1, sizeV - 1]

def GetTitleProper(title: str) -> Optional[str]:

    ##
    #
    # Retrieves the proper title of the story (removing parts like "(Part 6)" or "[Chapter 2]").
    #
    # @param title The title as it was retrieved from the web.
    #
    # @return The title proper.
    #
    ##

    if not title:
        return None

    titleProper = title

    titleProper = re.sub("\[?\(?Finale\)?\]?\.?", "", titleProper)
    titleProper = re.sub("\[?\(?Final part\)?\]?\.?", "", titleProper)
    titleProper = re.sub("\[?\(?Final update\)?\]?\.?", "", titleProper)
    titleProper = re.sub("\[?\(?Final\)?\]?\.?", "", titleProper)
    titleProper = re.sub("\[?\(?Chapter(\\s*)?(\d+)?\)?\]?\.?", "", titleProper)
    titleProper = re.sub("\[?\(?Part(\\s*)?(\d+)?\)?\]?\.?", "", titleProper)
    titleProper = re.sub("\[?\(?Update(\\s*)?(\d+)?\)?\]?\.?", "", titleProper)

    semicolonOccurence = titleProper.find(":")
    if -1 != semicolonOccurence:
        titleProper = titleProper[:semicolonOccurence]

    words = titleProper.split()
    if IsRomanNumeral(words[-1]):
        titleProper = " ".join(words[:-1])

    titleProper = titleProper.strip()

    return titleProper.strip()

def GetSubtitle(title: str) -> Optional[str]:

    ##
    #
    # Retrieves the proper subtitle of the story ("aaa: bbbbb" will return "bbbbb").
    #
    # @param title The title as it was retrieved from the web.
    #
    # @return The subtitle.
    #
    ##

    if not title:
        return None

    subtitle = title

    semicolonOccurence = subtitle.find(":")
    if -1 != semicolonOccurence:
        subtitle = subtitle[semicolonOccurence + 1:]

    subtitle = subtitle.strip()

    return subtitle

def IsRomanNumeral(text: str) -> bool:

    ##
    #
    # Checks if given string is a Roman numeral.
    #
    # @param text The input string.
    #
    # @return **True** if the string is a Roman numeral, **False** otherwise.
    #
    ##

    AllowedCharacters = [
        "I",
        "V",
        "X",
        "L",
        "C",
        "D",
        "M",
    ]

    text = text.strip()

    for character in text:

        if character not in AllowedCharacters:
            return False

    return True

def IsStringTrulyEmpty(text: str) -> bool:

    ##
    #
    # Checks whether a string is *truly* empty.
    #
    # A string is truly empty if its length is 0, or when it's composed solely of whitespace, or
    # when it doesn't exist at all.
    #
    # @param text The input string.
    #
    # @return **True** if the string is empty (according to the definition given above), **False**
    #         otherwise.
    #
    ##

    if (not text) or text.isspace():
        return True

    return False

def PrettifyDate(date: str) -> str:

    ##
    #
    # Returns a nicely formatted date.
    #
    # @param date The input date.
    #
    # @return Prettified input date.
    #
    ##

    if "?" == date:
        return date

    date = datetime.strptime(date, "%Y-%m-%d")

    return format_date(date, locale = "en")

def PrettifyNumber(number: int) -> str:

    ##
    #
    # Returns a nicely formatted number.
    #
    # @param number The input number.
    #
    # @return Prettified input number.
    #
    ##

    if 0 == number:
        return "?"

    return format_number(number, locale = "en")

def PrettifyTitle(
    title: str,
    removeContext: bool,
    unescape: bool
) -> str:

    ##
    #
    # Returns a prettified title.
    #
    # @param title         The input title.
    # @param removeContext Should we remove the context? (Like "Chapter 3: ".)
    # @param unescape      Should we resolve escaped HTML entities?
    #
    # @return Prettified input title.
    #
    ##

    if not title:
        return title

    if removeContext:
        title = re.sub(
            "\[?\(?Chapter \d+\:?\)?\]?\s*\.?-?\s*",
            "",
            title,
            flags = re.IGNORECASE
        )

    title = titlecase(title)

    if unescape:
        title = Unescape(title)

    return title

def Transliterate(string: str) -> str:

    ##
    #
    # Transliterates given string to ASCII.
    #
    # @param string The input string.
    #
    # @return The transliterated input string.
    #
    ##

    if not string:
        return string

    kakasi = pykakasi.kakasi()
    kakasi.setMode("H", "a")
    kakasi.setMode("K", "a")
    kakasi.setMode("J", "a")
    kakasi.setMode("r", "Hepburn")
    kakasi.setMode("s", True)
    kakasi.setMode("C", True)

    string = kakasi.getConverter().do(string)

    return string

def Truncate(string: str, length: int) -> str:

    ##
    #
    # Truncates a string to given length. Adds ellipsis at the end.
    #
    # @param string The string to be truncated.
    # @param length Maximum length of the output string.
    #
    # @return Truncated string.
    #
    ##

    if len(string) <= length:
        return string

    return string[:length - 1].rstrip() + "…"