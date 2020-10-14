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

# Standard packages.

import re
from typing import Optional

# Non-standard packages.

from dreamy_utilities.Text import IsRomanNumeral, IsStringEmpty
import pykakasi
from titlecase import titlecase

#
#
#
# Functions.
#
#
#

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

    # semicolonOccurence = titleProper.find(":")
    # if -1 != semicolonOccurence:
        # titleProper = titleProper[:semicolonOccurence]

    words = titleProper.split()
    if IsRomanNumeral(words[-1]):
        titleProper = " ".join(words[:-1])

    titleProper = titleProper.strip()

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