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
from fiction_dl.Utilities.Filesystem import GetPackageDirectory, ReadTextFile
from fiction_dl.Utilities.HTML import ReformatHTMLToXHTML

# Standard packages.

from pathlib import Path
from typing import Optional

# Non-standard packages.

from bs4 import BeautifulSoup
from ebooklib import epub

#
#
#
# Classes.
#
#
#

##
#
# The EPUB formatter.
#
##

class FormatterEPUB(Formatter):

    def __init__(
        self,
        embedImages: bool = True,
        coverImageData: Optional[bytes] = None
    ) -> None:

        ##
        #
        # The constructor.
        #
        # @param embedImages Embed images in the output file.
        #
        ##

        super().__init__(embedImages)

        self.CoverImageData = coverImageData

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

        # Create the e-book.

        book = epub.EpubBook()

        metadata = story.Metadata.GetPrettified()

        book.set_identifier(metadata.Title)
        book.set_title(metadata.Title)
        book.set_language("en")
        book.add_metadata("DC", "description", metadata.Summary)
        book.add_author(metadata.Author)

        # Set up the cover.

        if self.CoverImageData:
            book.set_cover(self._CoverImageName, self.CoverImageData)

        # Embed images.

        if self._embedImages:

            for index, image in enumerate(story.Images):

                if not image:
                    continue

                self._EmbedImage(book, f"{index}.jpeg", image.Data)

        # Prepare the spine.

        book.spine = ["cover", "nav"]

        # Add the metadata chapter.

        metadataFilePath = GetPackageDirectory() / "Templates/FormatterEPUB/Metadata.html"
        metadataTemplate = ReadTextFile(metadataFilePath)

        metadataChapter = epub.EpubHtml(
            file_name = "Metadata.xhtml",
            content = story.FillTemplate(metadataTemplate, escapeHTMLEntities = True),
            title = "Metadata",
            lang = "en"
        )

        book.add_item(metadataChapter)
        book.spine.append(metadataChapter)

        # Add the stylesheet.

        stylesheetFilePath = GetPackageDirectory() / "Templates/FormatterEPUB/Stylesheet.css"

        stylesheet = epub.EpubItem(
            uid = "style_default",
            file_name = "style/default.css",
            media_type = "text/css",
            content = ReadTextFile(stylesheetFilePath)
        )

        book.add_item(stylesheet)

        # Add chapters and create book spine.

        imageIndex = 0

        for index, chapter in enumerate(story.Chapters, start = 1):

            def TitleTextGenerator(index: int, title: str) -> str:
                return f"Chapter {index}" + (f": {title}" if title else "")

            def Prefixer(index: int, title: str) -> str:
                return f"<h1>{TitleTextGenerator(index, title)}</h1>"

            # Create the chapter.

            bookChapter = epub.EpubHtml(
                file_name = f"Chapter {index}.xhtml",
                title = TitleTextGenerator(index, chapter.Title),
                lang = "en"
            )

            # Prepare chapter content.

            content = Prefixer(index, chapter.Title) + chapter.Content
            content = ReformatHTMLToXHTML(content)

            if self.CoverImageData and (len(story.Chapters) == index):
                content += f'<img src = "{self._CoverImageName}"/>'

            # Replace images.

            if self._embedImages:

                soup = BeautifulSoup(content, features = "html.parser")

                for tag in soup.find_all("img"):

                    tag["src"] = f"{index}.jpeg"
                    tag["alt"] = "There is an image here."

                    imageIndex += 1

                content = str(soup)

            else:

                content = content.replace("<img/>", "")

            # Set the chapter.

            bookChapter.set_content(content)

            book.add_item(bookChapter)
            book.spine.append(bookChapter)

        # Create a ToC.

        book.toc = book.spine[1:]

        # Add NCX and Navigation tile.

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Write the file.

        epub.write_epub(filePath, book, {})

        # Return.

        return True

    @staticmethod
    def _EmbedImage(
        book: epub.EpubBook,
        fileName: str,
        data: bytes,
        fileType: str = "image/jpeg"
    ) -> bool:

        ##
        #
        # Embeds an image inside the created ebook.
        #
        # @param book     The ebook.
        # @param fileName Embedded image's file name (that is, the file name of the image file
        #                 *inside* the ebook archive).
        # @param data     Image data: binary and encoded.
        # @param fileType Image data type.
        #
        # @return **True** if the image has been embedded correctly, **False** otherwise.
        #
        ##

        if (not book) or (not fileName) or (not data) or (not fileType):
            return False

        item = epub.EpubImage()
        item.file_name = fileName
        item.media_type = fileType
        item.content = data

        book.add_item(item)

        return True

    _CoverImageName = "Cover.jpeg"