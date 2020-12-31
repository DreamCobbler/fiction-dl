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
from fiction_dl.Concepts.StoryPackage import StoryPackage
from fiction_dl.Utilities.Filesystem import GetPackageDirectory

# Standard packages.

from base64 import b64encode
from pathlib import Path
from typing import List, Union

# Non-standard packages.

from bs4 import BeautifulSoup
from dreamy_utilities.Filesystem import ReadTextFile

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

        # Choose the appropriate template file.

        templateFileName =                          \
            "FormatterHTML (Package).html"          \
            if isinstance(story, StoryPackage) else \
            "FormatterHTML.html"

        # Load the template and fill it with the story.

        templateFilePath = GetPackageDirectory() / f"Templates/{templateFileName}"
        content = story.FillTemplate(ReadTextFile(templateFilePath), escapeHTMLEntities = True)

        def ChapterTitler(index: int, chapterTitle: str) -> str:
            return f"Chapter {index}" + (f": {chapterTitle}" if chapterTitle else "")

        def PackagePrefixer(index: int, chapterTitle: str, storyTitle: str) -> str:
            return f"<h2>{storyTitle} — {ChapterTitler(index, chapterTitle)}</h2>"

        def StoryPrefixer(index: int, chapterTitle: str, storyTitle: str) -> str:
            return f"<h2>{ChapterTitler(index, chapterTitle)}</h2>"

        prefixer = PackagePrefixer if isinstance(story, StoryPackage) else StoryPrefixer
        content = content.replace(
            "@@@Content@@@",
            story.Join(prefixer)
        )

        # Replace images.

        if self._embedImages:

            soup = BeautifulSoup(content, features = "html.parser")

            for index, tag in enumerate(soup.find_all("img")):

                if (0 == index) or (index > len(story.Images)):
                    continue

                if (image := story.Images[index - 1]):
                    tag["src"] = "data:image/jpeg;base64," + b64encode(image.Data).decode()
                    tag["alt"] = "There is an image here."
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