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
from fiction_dl.Utilities.HTML import StripEmptyTags

# Standard packages.

import html
from pathlib import Path
import re
from typing import List, Union
from zipfile import ZipFile, is_zipfile, ZIP_DEFLATED

# Non-standard packages.

from bs4 import BeautifulSoup
from dreamy_utilities.Filesystem import ReadTextFile
from dreamy_utilities.Mathematics import GetDimensionsToFit
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
# The ODT formatter.
#
##

class FormatterODT(Formatter):

    def __init__(self, embedImages: bool = True, combinedVersion: bool = False) -> None:

        ##
        #
        # The constructor.
        #
        # @param embedImages     Embed images in the output file.
        # @param combinedVersion Use the template designed for multiple stories.
        #
        ##

        super().__init__(embedImages)

        # Intialize member variables.

        templateFileName =                        \
            "Templates/FormatterODT/Template.odt" \
            if not combinedVersion else           \
            "Templates/FormatterODT/Template (Combined).odt"

        self._templateFilePath = GetPackageDirectory() / templateFileName

        self._manifestDocument = ""
        self._contentDocument = ""
        self._metadataDocument = ""
        self._stylesDocument = ""

        # Load the template.

        with ZipFile(self._templateFilePath, "r") as archive:

            self._manifestDocument = Stringify(archive.read("META-INF/manifest.xml"))
            self._contentDocument = Stringify(archive.read("content.xml"))
            self._metadataDocument = Stringify(archive.read("meta.xml"))
            self._stylesDocument = Stringify(archive.read("styles.xml"))

        # Modify the styles.

        EOF = self._stylesDocument.find("</office:styles>")

        styles = ReadTextFile(GetPackageDirectory() / "Templates/FormatterODT/Styles.xml")
        self._stylesDocument = self._stylesDocument[:EOF] + styles + self._stylesDocument[EOF:]

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

        # Retrieve story content and translate it to ODT-compatible XML.

        def ChapterTitler(index: int, chapterTitle: str) -> str:
            return f"Chapter {index}" + (f": {chapterTitle}" if chapterTitle else "")

        def PackagePrefixer(index: int, chapterTitle: str, storyTitle: str) -> str:
            return f"<h1>{storyTitle} — {ChapterTitler(index, chapterTitle)}</h1>"

        def StoryPrefixer(index: int, chapterTitle: str, storyTitle: str) -> str:
            return f"<h1>{ChapterTitler(index, chapterTitle)}</h1>"

        prefixer = PackagePrefixer if isinstance(story, StoryPackage) else StoryPrefixer

        content = self._TranslateHTMLtoODT(story.Join(prefixer), story)
        content = StripEmptyTags(
            content,
            validEmptyTags = ["draw:frame", "draw:image"],
            validEmptyTagAttributes = {"text:style-name": "Horizontal_20_Line"}
        )

        # Prepare the files.

        manifestDocument = self._manifestDocument
        contentDocument = self._contentDocument
        metadataDocument = self._metadataDocument
        stylesDocument = self._stylesDocument

        # Modify the content.

        metadata = story.Metadata.GetPrettified(escapeHTMLEntities = True)

        contentDocument = story.FillTemplate(contentDocument, escapeHTMLEntities = True)
        contentDocument = contentDocument.replace("http://link.link/", metadata.URL)

        EOF = contentDocument.find("</office:text>")
        contentDocument = contentDocument[:EOF] + content + contentDocument[EOF:]

        # Modify the metadata.

        EOF = "</office:meta>"

        metadataDocument = self._SetTagContent(
            metadataDocument,
            "dc:title",
            html.escape(metadata.Title),
            EOF
        )

        metadataDocument = self._SetTagContent(
            metadataDocument,
            "meta:initial-creator",
            html.escape(metadata.Author),
            EOF
        )

        metadataDocument = self._SetTagContent(
            metadataDocument,
            "dc:creator",
            html.escape(metadata.Author),
            EOF
        )

        # Modify the styles.

        stylesDocument = story.FillTemplate(stylesDocument, escapeHTMLEntities = True)

        # Modify the manifest.

        if self._embedImages:

            for index, image in enumerate(story.Images):

                if not image.Data:
                    continue

                EOF = manifestDocument.find("</manifest:manifest>")
                manifestDocument = manifestDocument[:EOF] + \
                    '<manifest:file-entry manifest:full-path="Pictures/{}.jpeg"' \
                    ' manifest:media-type="image/jpeg"/>'.format(index) + \
                    manifestDocument[EOF:]

        # Save the output file.

        ReplacedFilesNames = [
            "META-INF/manifest.xml",
            "content.xml",
            "meta.xml",
            "styles.xml"
        ]

        with ZipFile(filePath, mode = "a") as outputArchive:

            with ZipFile(self._templateFilePath, "r") as archive:

                for item in [x for x in archive.infolist() if x.filename not in ReplacedFilesNames]:
                    outputArchive.writestr(item, archive.read(item.filename))

            outputArchive.writestr("META-INF/manifest.xml", manifestDocument)
            outputArchive.writestr("content.xml", contentDocument)
            outputArchive.writestr("meta.xml", metadataDocument)
            outputArchive.writestr("styles.xml", stylesDocument)

            if self._embedImages:

                for index, image in enumerate(story.Images):

                    if not image:
                        continue

                    outputArchive.writestr(f"Pictures/{index}.jpeg", image.Data)

        # Return.

        return True

    @staticmethod
    def _SetTagContent(
        document: str,
        tagName: str,
        newValue: str,
        EOF: str
    ) -> str:

        ##
        #
        # Replaces XML tag contents.
        #
        # @param document XML code.
        # @param tagName Tag name.
        # @param newValue Desired tag value.
        # @param EOF A string designating end-of-file.
        #
        # @return Modified code.
        #
        ##

        openingTag = f"<{tagName}>"
        closingTag = f"</{tagName}>"
        tagWithValue = f"{openingTag}{newValue}{closingTag}"

        if -1 != (tagPosition := document.find(openingTag)):

            document = re.sub(
                f"{openingTag}(.*){closingTag}",
                tagWithValue,
                document
            )

        elif -1 != (EOF := document.find(EOF)):

            document = document[:EOF] + tagWithValue + document[EOF:]

        # Return.

        return document

    def _TranslateHTMLtoODT(self, code: str, story: Union[Story, StoryPackage]) -> str:

        ##
        #
        # Translates HTML code to ODT code.
        #
        # @param code HTML code.
        #
        # @return ODT code.
        #
        ##

        # Process the content.

        soup = BeautifulSoup(code, features = "html.parser")

        imageIndex = 0

        for tag in soup.find_all(True, recursive = True):

            if "h1" == tag.name:

                tag.name = "text:h"
                tag["text:style-name"] = "Imported_Chapter"
                tag["text:outline-level"] = "1"

            elif "hr" == tag.name:

                tag.name = "text:p"
                tag["text:style-name"] = "Horizontal_20_Line"

            elif "p" == tag.name:

                tag.name = "text:p"
                tag["text:style-name"] = "Text_20_body"

            elif tag.name in ["b", "strong"]:

                tag.name = "text:span"
                tag["text:style-name"] = "Imported_Bold"

            elif tag.name in ["i", "em"]:

                tag.name = "text:span"
                tag["text:style-name"] = "Imported_Emphasis"

            elif "u" == tag.name:

                tag.name = "text:span"
                tag["text:style-name"] = "Imported_Underline"

            elif "a" == tag.name:

                if tag.has_attr("href"):

                    tag.name = "text:a"
                    tag["xlink:type"] = "simple"
                    tag["xlink:href"] = tag["href"]
                    tag["text:style-name"] = "Internet_20_link"
                    tag["text:visited-style-name"] = "Visited_20_Internet_20_Link"

                    del tag["href"]

                else:

                    tag.replaceWith("")

            elif ("img" == tag.name):

                if (not self._embedImages) or (imageIndex >= len(story.Images)):
                    tag.replaceWith("")
                    continue

                image = story.Images[imageIndex]
                if not image:
                    tag.replaceWith("")
                    continue

                maximumWidth = 17 # cm
                maximumHeight = 17 # cm
                width, height = GetDimensionsToFit(
                    (image.W, image.H),
                    (maximumWidth, maximumHeight)
                )

                drawFrameTag = soup.new_tag("draw:frame")
                drawFrameTag["draw:style-name"] = "Imported_Image"
                drawFrameTag["draw:name"] = f"Image{imageIndex}"
                drawFrameTag["text:anchor-type"] = "char"
                drawFrameTag["svg:width"] = "{:.3f}cm".format(width)
                drawFrameTag["svg:height"] = "{:.3f}cm".format(height)
                drawFrameTag["draw:z-index"] = "1"

                drawImageTag = soup.new_tag("draw:image")
                drawImageTag["xlink:href"] = f"Pictures/{imageIndex}.jpeg"
                drawImageTag["xlink:type"] = "simple"
                drawImageTag["xlink:show"] = "embed"
                drawImageTag["xlink:actuate"] = "onLoad"
                drawImageTag["loext:mime-type"] = "image/jpeg"
                drawFrameTag.append(drawImageTag)

                tag.replace_with(drawFrameTag)

                imageIndex += 1

        return str(soup)