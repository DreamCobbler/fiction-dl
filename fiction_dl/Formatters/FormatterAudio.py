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

from fiction_dl.Concepts.Formatter import Formatter
from fiction_dl.Concepts.Story import Story
from fiction_dl.Concepts.StoryPackage import StoryPackage
from fiction_dl.Utilities.Text import GetPrintableStoryTitle

# Standard packages.

from pathlib import Path
import shutil
from typing import Union

# Non-standard packages.

from bs4 import BeautifulSoup
from dreamy_utilities.Filesystem import GetUniqueFileName
import pyttsx3

#
#
#
# Classes.
#
#
#

##
#
# The audiobook formatter. (Well, "formatter".)
#
##

class FormatterAudio(Formatter):

    def __init__(self) -> None:

        ##
        #
        # The constructor.
        #
        ##

        super().__init__(False)

    def FormatAndSaveToDirectory(self, story: Union[Story, StoryPackage], directoryPath: Path) -> bool:

        ##
        #
        # Formats the story (or the story package) and saves it to the output directory.
        #
        # @param story         The story/story package to be formatted and saved.
        # @param directoryPath The path in which output files will be stored.
        #
        # @return **True** if the output files were generated and saved without problems, **False**
        #         otherwise.
        #
        ##

        # Create the output directory.

        directoryPath.mkdir(parents = True, exist_ok = True)

        # Create and set up the engine.

        engine = pyttsx3.init()

        engine.setProperty("rate", 125)
        engine.setProperty("voice", engine.getProperty("voices")[1].id)

        # Generate the text of the story.

        for index, chapter in enumerate(story.Chapters, start = 1):

            text = ""

            prettifiedMetadata = story.Metadata.GetPrettified()
            text += f"{prettifiedMetadata.Title}, by {prettifiedMetadata.Author}\n"

            if 1 == index:
                text += f"Summary: {prettifiedMetadata.Summary}\n"

            text += f"Chapter {index}" + (f": {chapter.Title}" if chapter.Title else "")
            text += "\n"

            text += BeautifulSoup(chapter.Content, features = "html.parser").get_text().strip()

            # Save the output file.

            temporaryFileName = f"{GetUniqueFileName()}.mp3"

            engine.save_to_file(
                text,
                temporaryFileName
            )

            engine.runAndWait()

            outputFileName = f"{GetPrintableStoryTitle(story)} - Chapter {index}.mp3"
            shutil.move(temporaryFileName, directoryPath / outputFileName)

        # Return.

        return True

    def FormatAndSave(self, story: Union[Story, StoryPackage], filePath: Path) -> bool:

        ##
        #
        # Formats the story (or the story package) and saves it to the output file.
        #
        # @param story    The story/story package to be formatted and saved.
        # @param filePath The path to the output file.
        #
        # @return **True** if the output file was generated and saved without problems, **False**
        #         otherwise.
        #
        ##

        # Create and set up the engine.

        engine = pyttsx3.init()

        engine.setProperty("rate", 125)
        engine.setProperty("voice", engine.getProperty("voices")[1].id)

        # Generate the text of the story.

        text = ""

        prettifiedMetadata = story.Metadata.GetPrettified()
        text += f"{prettifiedMetadata.Title}, by {prettifiedMetadata.Author}"
        text += "\n"
        text += f"Summary: {prettifiedMetadata.Summary}"
        text += "\n"

        for index, chapter in enumerate(story.Chapters, start = 1):

            text += f"Chapter {index}"
            if chapter.Title:
                text += f": {chapter.Title}"
            text += "\n"

            text += BeautifulSoup(chapter.Content, features = "html.parser").get_text().strip()

        # Save the output file.

        temporaryFileName = f"{GetUniqueFileName()}.mp3"

        engine.save_to_file(
            text,
            temporaryFileName
        )

        engine.runAndWait()

        shutil.move(temporaryFileName, filePath)

        # Return.

        return True