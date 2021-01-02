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

from fiction_dl.Concepts.Story import Story

# Standard packages.

import re
from typing import Optional

# Non-standard packages.

from dreamy_utilities.Filesystem import GetSanitizedFileName
from dreamy_utilities.Text import IsRomanNumeral, IsStringEmpty, PrettifyTitle
import pykakasi

#
#
#
# Functions.
#
#
#

def GetPrintableStoryTitle(story: Story) -> str:

    prettifiedMetadata = story.Metadata.GetPrettified()

    title = Transliterate(prettifiedMetadata.Title)
    title = GetSanitizedFileName(title)
    title = re.sub("\s+", " ", title)

    return title.strip()

def GetTitleProper(title: str) -> Optional[str]:

    ##
    #
    # Retrieves the proper title of the story (removing things like parts after a semicolon).
    #
    # @param title The full title.
    #
    # @return The title proper.
    #
    ##

    if not title:
        return None

    titleProper = PrettifyTitle(title, removeContext = True)

    if titleProper.endswith("?") or titleProper.endswith(".") or titleProper.endswith("!"):
        titleProper = titleProper[:-1]

    separatorOccurence = titleProper.find(":")
    if -1 != separatorOccurence:
        titleProper = titleProper[:separatorOccurence]

    separatorOccurence = titleProper.find(".")
    if -1 != separatorOccurence:
        titleProper = titleProper[:separatorOccurence]

    separatorOccurence = titleProper.find("?")
    if -1 != separatorOccurence:
        titleProper = titleProper[:separatorOccurence]

    separatorOccurence = titleProper.find("!")
    if -1 != separatorOccurence:
        titleProper = titleProper[:separatorOccurence]

    words = titleProper.split()
    if IsRomanNumeral(words[-1]):
        titleProper = " ".join(words[:-1])

    return titleProper.strip()

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