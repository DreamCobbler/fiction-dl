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

# Standard packages.

from pathlib import Path

# Non-standard packages.

import fitz

#
#
#
# Functions.
#
#
#

def RenderPDFPageToBytes(documentFilePath: Path, pageIndex: int) -> bytes:

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