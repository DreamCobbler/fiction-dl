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

from datetime import date, datetime
from pathlib import Path
import sys
from typing import Any, List, Optional, Tuple

# Non-standard packages.

import fitz # Requires PyMuPDF.

#
#
#
# Functions.
#
#
#

def Bytify(value: Any) -> Optional[bytes]:

    ##
    #
    # Converts any value to "bytes".
    #
    # @param value The data to be bytified.
    #
    # @return Bytified input value.
    #
    ##

    if value is None:
        return value

    elif isinstance(value, bytes):
        return value

    else:
        return bytes(value, encoding = "utf-8")

def Stringify(value: Any) -> Optional[str]:

    ##
    #
    # Converts any value to "str".
    #
    # @param value The data to be stringified.
    #
    # @return Stringified input value.
    #
    ##

    if value is None:
        return value

    elif isinstance(value, str):
        return value

    elif isinstance(value, bytes):
        return value.decode("utf-8")

    else:
        return str(value)

def GetCurrentDate() -> str:

    ##
    #
    # Returns today's date, in ISO 8601 format.
    #
    # @return Today's date.
    #
    ##

    return date.today().isoformat()

def GetDateFromTimestamp(timestamp: str) -> Optional[str]:

    ##
    #
    # Converts Unix timestamp to ISO 8601 date.
    #
    # @param timestamp The input timestamp.
    #
    # @return The input date converted to ISO 8601 date format (YYYY-MM-DD).
    #
    ##

    if not timestamp:
        return None

    return date.fromtimestamp(timestamp).isoformat()

def GetDimensionsToFit(
    width: int,
    height: int,
    outsideWidth: int,
    outsideHeight: int
) -> Tuple[int, int]:

    ##
    #
    # Proportionally scales a rectangle to fit inside another rectangle.
    #
    # @param width         The width of the inside rectangle.
    # @param height        The height of the inside rectangle.
    # @param outsideWidth  The width of the outside rectangle.
    # @param outsideHeight The height of the outside rectangle.
    #
    # @return A tuple containing new dimensions for the inside rectangle: (W, H).
    #
    ##

    if (0 == width) or (0 == height):
        return (0, 0)

    scale = min(
        outsideWidth / width,
        outsideHeight / height
    )

    return (
        int(scale * width),
        int(scale * height)
    )

def RemoveDuplicates(input: List[Any]) -> List[Any]:

    ##
    #
    # Removes duplicates from a list while preserving its order.
    #
    # @param input A list.
    #
    # @return The same list, with duplicates removed.
    #
    ##

    return list(dict.fromkeys(input))

def RenderPageToBytes(documentFilePath: Path, pageIndex: int) -> bytes:

    ##
    #
    # Renders given page of a PDF document to image, then returns the image data.
    #
    # @param documentFilePath The path to the document in question.
    # @param pageIndex        Index of the page to be rendered.
    #
    # @return Encoded image data, in JPEG format.
    #
    ##

    document = fitz.open(documentFilePath)
    page = document.loadPage(pageIndex)

    return page.getPixmap().getImageData(output = "jpeg")