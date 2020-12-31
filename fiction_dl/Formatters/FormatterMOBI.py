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

from fiction_dl.Concepts.Formatter import Formatter
from fiction_dl.Concepts.Story import Story

# Standard packages.

from pathlib import Path
from subprocess import call, DEVNULL

# Non-standard packages.

from dreamy_utilities.Text import Stringify

#
#
#
# Classes.
#
#
#

##
#
# The MOBI formatter.
#
##

class FormatterMOBI(Formatter):

    def __init__(self, embedImages: bool = True) -> None:

        ##
        #
        # The constructor.
        #
        # @param embedImages Embed images in the output file.
        #
        ##

        super().__init__(embedImages)

    def FormatAndSave(self, story: Story, filePath: Path) -> bool:

        ##
        #
        # Formats the story and saves it to the output file. This function is currently **not
        # implemented**.
        #
        # @param story    The story to be formatted and saved.
        # @param filePath The path to the output file.
        #
        # @return **True** if the output file was generated and saved without problems, **False**
        #         otherwise.
        #
        ##

        raise NotImplementedError()

    def ConvertFromEPUB(
        self,
        sourceFilePath: Path,
        outputDirectoryPath: Path
    ) -> bool:

        ##
        #
        # Converts an EPUB file to a MOBI file. The output file may exist: it will be overwritten if
        # it does.
        #
        # @param sourceFilePath      Path to the EPUB file.
        # @param outputDirectoryPath Path to the output directory. The output file will be created
        #                            inside it; its (base)name will be the same as the name of the
        #                            source file. The directory **has** to exist beforehand, this
        #                            method does *not* create it.
        #
        # @return **True** if the conversion has been performed successfully, **False** otherwise.
        #
        ##

        if not sourceFilePath.is_file():
            return False

        elif not outputDirectoryPath.is_dir():
            return False

        call(
            [
                "ebook-convert",
                Stringify(sourceFilePath),
                Stringify(outputDirectoryPath / (sourceFilePath.stem + ".mobi")),
            ],
            stdout = DEVNULL,
            stderr = DEVNULL
        )

        return True