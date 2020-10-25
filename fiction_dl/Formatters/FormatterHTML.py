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
from fiction_dl.Utilities.Filesystem import GetPackageDirectory

# Standard packages.

from base64 import b64encode
from pathlib import Path
from typing import List

# Non-standard packages.

from bs4 import BeautifulSoup
from dreamy_utilities.Filesystem import ReadTextFile
from dreamy_utilities.Text import PrettifyNumber

#
#
#
# Classes.
#
#
#

##
#
# The HTML formatter.
#
##

class FormatterHTML(Formatter):

    def __init__(self, embedImages: bool = True) -> None:

        ##
        #
        # The constructor.
        #
        # @param embedImages Embed images in the output file.
        #
        ##

        super().__init__(embedImages)

    def FormatAndSaveCombined(
        self,
        stories: List[Story],
        title: str,
        filePath: Path
    ) -> bool:

        ##
        #
        # Formats multiple stories and saves them in the output file.
        #
        # @param stories  The list of stories to be combined.
        # @param title    The title of the created package of stories.
        # @param filePath The path to the output file.
        #
        # @return **True** if the output file was generated and saved without problems, **False**
        #         otherwise.
        #
        ##

        # Combine all the stories provided.

        combinedContent = ""

        combinedChapterCount = 0
        combinedWordCount = 0

        for story in stories:

            storyTitle = story.Metadata.GetPrettified().Title

            def Prefixer(index: int, title: str) -> str:
                return "<h3>" + f"{storyTitle} — Chapter {index}" + (f": {title}" if title else "") + "</h3>"

            combinedContent += f"<h2>{storyTitle}</h2>" + story.Join(Prefixer)

            combinedChapterCount += story.Metadata.ChapterCount
            combinedWordCount += story.Metadata.WordCount

        # Load the template and fill it with the story.

        templateFilePath = GetPackageDirectory() / "Templates/FormatterHTML (Combined).html"

        content = ReadTextFile(templateFilePath)
        content = content.replace("@@@Title@@@", title)
        content = content.replace("@@@ChapterCount@@@", PrettifyNumber(combinedChapterCount))
        content = content.replace("@@@WordCount@@@", PrettifyNumber(combinedWordCount))
        content = content.replace("@@@StoryCount@@@", PrettifyNumber(len(stories)))
        content = content.replace("@@@Content@@@", combinedContent)

        content = stories[0].FillTemplate(content, escapeHTMLEntities = True)

        # Save the template to file.

        try:

            with open(filePath, "w", encoding = "utf-8") as outputFile:
                outputFile.write(content)

            return True

        except OSError:

            return False

    def FormatAndSave(self, story: Story, filePath: Path) -> bool:

        ##
        #
        # Formats the story and saves it to the output file.
        #
        # @param story    The story to be formatted and saved.
        # @param filePath The path to the output file.
        #
        # @return **True** if the output file was generated and saved without problems, **False**
        #         otherwise.
        #
        ##

        # Load the template and fill it with the story.

        templateFilePath = GetPackageDirectory() / "Templates/FormatterHTML.html"
        content = story.FillTemplate(ReadTextFile(templateFilePath), escapeHTMLEntities = True)

        def Prefixer(index: int, title: str) -> str:
            return "<h2>" + f"Chapter {index}" + (f": {title}" if title else "") + "</h2>"

        content = content.replace("@@@Content@@@", story.Join(Prefixer))

        # Replace images.

        if self._embedImages:

            soup = BeautifulSoup(content, features = "html.parser")

            for index, tag in enumerate(soup.find_all("img")):

                if index >= len(story.Images):
                    continue

                if (image := story.Images[index]):

                    tag["src"] = "data:image/jpeg;base64," + b64encode(image.Data).decode()

                else:

                    tag["alt"] = "There ought to be an image here."

            content = str(soup)

        else:

            content = content.replace("<img/>", "")

        # Save the template to file.

        try:

            with open(filePath, "w", encoding = "utf-8") as outputFile:
                outputFile.write(content)

            return True

        except OSError:

            return False