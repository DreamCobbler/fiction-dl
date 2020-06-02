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

from typing import Optional

# Non-standard packages.

import cv2
import numpy

#
#
#
# Classes.
#
#
#

##
#
# Represents an image.
#
##

class Image:

    def __init__(self, URL: str) -> None:

        ##
        #
        # The constructor.
        #
        # @param URL The image's URL.
        #
        ##

        self.URL = URL

        self.Data = None
        self.W = None
        self.H = None

    def CreateFromData(self, data: bytes, side: Optional[int] = None, quality: int = 75) -> bool:

        ##
        #
        # Creates an image from binary data (decoding it using OpenCV). The image is then optionally
        # scaled down to fit the maximum side length provided as an argument.
        #
        # @param data    Encoded image data.
        # @param side    The maximum length of the longer side of the image. The image
        #                will be scaled down proportionally to fit.
        # @param quality The quality of the output image (1 - 100).
        #
        # @return **True** if the image has been created correctly, **False** otherwise.
        #
        ##

        if not data:
            return False

        # Decode the image.

        image = cv2.imdecode(numpy.frombuffer(data, dtype = numpy.uint8), flags = -1)
        if (image is None) or (0 == image.size):
            return False

        height = image.shape[0]
        width = image.shape[1]
        if (not height) or (not width):
            return False

        # Scale down the image (if necessary).

        if side and (scale := side / max(width, height)) < 1:
            image = cv2.resize(
                image,
                (int(scale * width), int(scale * height)),
                interpolation = cv2.INTER_LANCZOS4
            )

        # Encode image data and store it.

        _, encodedImage = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        convertedData = numpy.array(encodedImage).tobytes()

        if not convertedData:
            return False

        self.Data = convertedData
        self.W = width
        self.H = height

        return True

    def __bool__(self) -> bool:

        ##
        #
        # The bool operator.
        #
        # @return **True** if the image exists (i.e. has data), **False** otherwise. An image that
        #         has its URL defined, but possesses no content doesn't exist (returns **False**).
        #
        ##

        return bool(self.Data)