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

from fiction_dl.Concepts.Chapter import Chapter
from fiction_dl.Concepts.Story import Story
from fiction_dl.Core.Cache import Cache
from fiction_dl.Core.InputData import InputData
from fiction_dl.Core.Interface import Interface
from fiction_dl.Extractors.ExtractorTextFile import ExtractorTextFile
from fiction_dl.Formatters.FormatterEPUB import FormatterEPUB
from fiction_dl.Formatters.FormatterHTML import FormatterHTML
from fiction_dl.Formatters.FormatterMOBI import FormatterMOBI
from fiction_dl.Formatters.FormatterODT import FormatterODT
from fiction_dl.Formatters.FormatterPDF import FormatterPDF
from fiction_dl.Processors.SanitizerProcessor import SanitizerProcessor
from fiction_dl.Processors.TypographyProcessor import TypographyProcessor
from fiction_dl.Utilities.Extractors import CreateExtractor
from fiction_dl.Utilities.Filesystem import FindEbookConvert, SanitizeFileName, WriteTextFile
from fiction_dl.Utilities.General import RemoveDuplicates, RenderPageToBytes, Stringify
from fiction_dl.Utilities.HTML import FindImagesInCode, MakeURLAbsolute
from fiction_dl.Utilities.Text import Transliterate, Truncate
from fiction_dl.Utilities.Web import GetSiteURL
import fiction_dl. Configuration as Configuration

# Standard packages.

from argparse import Namespace
import logging
from os.path import expandvars, isfile
from pathlib import Path
import re
from requests.exceptions import ConnectionError
from time import sleep
from typing import Dict, List
from urllib3.exceptions import ProtocolError

# Non-standard packages.

import termtables

#
#
#
# Classes.
#
#
#

##
#
# The "Application" class encapsulates the whole logic of the application.
#
##

class Application:

    def __init__(self, arguments: Namespace, cacheDirectoryPath: Path) -> None:

        ##
        #
        # The constructor.
        #
        # @param cacheDirectoryPath The path to the cache directory.
        #
        ##

        self._arguments = arguments

        self._cache = Cache(cacheDirectoryPath)
        self._interface = Interface()

    def Launch(self) -> None:

        ##
        #
        # Launches the application.
        #
        ##

        # Welcome the user and clear the cache.

        self._interface.Text(Configuration.WelcomingMessage, bold = True)

        if self._arguments.ClearCache:
            logging.info("Deleting the cache...")
            self._cache.Clear()

        # Print notices.

        if (notices := self._GenerateNotices()):

            self._interface.EmptyLine()

            for notice in notices:
                self._interface.Notice(notice)

        # Process the input arguments.

        self._interface.Process("Processing input arguments...", section = True)

        inputData = InputData(self._arguments.Input)
        inputData.ExpandAndShuffle()

        URLs = inputData.Access()

        self._interface.Comment(f"The list contains {len(URLs)} item(s).")

        # Process the stories.

        skippedURLs = []

        for index, URL in enumerate(URLs, start = 1):

            self._interface.LineBreak()
            self._interface.Text(f'{index}/{len(URLs)}: "{URL}".', section = True, bold = True)

            successfullyProcessedURL = False

            try:

                successfullyProcessedURL = self._ProcessURL(URL)

            except KeyboardInterrupt:

                self._interface.ClearLine()
                self._interface.Notice("Quitting...")

                exit()

            except ConnectionError as caughtException:

                self._interface.Error(f"The website has refused connection: {caughtException}")

            except BaseException as caughtException:

                self._interface.Error(f"An exception has been thrown: {caughtException}")

            except:

                self._interface.Error("An exception has been thrown.")

            if not successfullyProcessedURL:
                skippedURLs.append(URL)

        self._interface.LineBreak()

        # Print information about skipped stories.

        if skippedURLs:

            print()

            for URL in skippedURLs:
                self._interface.Error(f'Failed to download a story: "{URL}".')

            WriteTextFile(Configuration.SkippedURLsFilePath, "\n".join(skippedURLs))

        # Print some final information.

        successCount = len(URLs) - len(skippedURLs)

        self._interface.Comment(f"Downloaded {successCount}/{len(URLs)} stories.", section = True)

        # Clear the cache.

        if not self._arguments.PersistentCache:
            logging.info("Deleting the cache...")
            self._cache.Clear()

    def _ProcessURL(self, URL: str) -> bool:

        ##
        #
        # Processes a URL, in text mode.
        #
        # @param URL The URL to be processed.
        #
        # @return **True** if the URL has been processed successfully, **False** otherwise.
        #
        ##

        # Locate a working extractor.

        self._interface.Process("Creating the extractor...", section = True)

        extractor = CreateExtractor(URL)
        if not extractor:
            logging.error("No matching extractor found.")
            return False

        self._interface.Comment(f'Extractor created: "{type(extractor).__name__}".')

        # Authenticate the user (if supported by the extractor).

        if self._arguments.Authenticate and extractor.SupportsAuthentication():

            if not extractor.Authenticate():
                self._interface.Error("Failed to authenticate.")

            else:
                self._interface.Comment("Authenticated successfully.")

        # Scan the story.

        self._interface.Process("Scanning the story...", section = True)

        if not extractor.ScanStory():
            logging.error("Failed to scan the story.")
            return False

        self._PrintMetadata(extractor.Story)

        # Check whether the output files already exist.

        outputFilePaths = self._GetOutputFilePaths(self._arguments.Output, extractor.Story)

        if (not self._arguments.Force) and all(x.is_file() for x in outputFilePaths.values()):
            self._interface.Comment("This story has been downloaded already.", section = True)
            return True

        elif self._arguments.Force:
            [x.unlink() for x in outputFilePaths.values() if x.is_file()]

        # Extract content.

        self._interface.Process("Extracting content...", section = True)

        for index in range(1, extractor.Story.Metadata.ChapterCount + 1):

            # Generate cache identifiers.

            cacheOwnerName = extractor.Story.Metadata.URL
            cacheTitleName = f"{index}-Title"
            cacheContentName = f"{index}-Content"

            # Retrieve chapter data, either from cache or by downloading it.

            retrievedFromCache = False

            chapter = Chapter(
                title = Stringify(self._cache.RetrieveItem(cacheOwnerName, cacheTitleName)),
                content = Stringify(self._cache.RetrieveItem(cacheOwnerName, cacheContentName))
            )

            if chapter:

                retrievedFromCache = True

            else:

                chapter = extractor.ExtractChapter(index)

                if not chapter:
                    logging.error("Failed to extract story content.")
                    return False

            extractor.Story.Chapters.append(chapter)

            # Add the chapter to cache.

            if not retrievedFromCache:
                self._cache.AddItem(cacheOwnerName, cacheTitleName, chapter.Title)
                self._cache.AddItem(cacheOwnerName, cacheContentName, chapter.Content)

            # Notify the user, then sleep for a while.

            self._interface.ProgressBar(
                index,
                extractor.Story.Metadata.ChapterCount,
                Configuration.ProgressBarLength,
                f"# Extracted chapter {index}/{extractor.Story.Metadata.ChapterCount}",
                True
            )

            if extractor.Story.Metadata.ChapterCount == index:
                self._interface.EmptyLine()

            if not retrievedFromCache:
                sleep(Configuration.PostChapterSleepTime)

        # Locate and download images.

        if self._arguments.Images:

            self._interface.Process("Downloading images...", section = True)

            # Locate the images.

            for chapter in extractor.Story.Chapters:
                extractor.Story.Images.extend(FindImagesInCode(chapter.Content))

            storySiteURL = GetSiteURL(extractor.Story.Metadata.URL)
            for image in extractor.Story.Images:
                image.URL = MakeURLAbsolute(image.URL, storySiteURL)

            self._interface.Comment(f"Found {len(extractor.Story.Images)} image(s).")

            # Download them.

            if extractor.Story.Images:

                imageCount = len(extractor.Story.Images)
                downloadedImageCount = 0

                previousImageFailedToDownlod = False

                for index, image in enumerate(extractor.Story.Images, start = 1):

                    retrievedFromCache = False
                    imageData = self._cache.RetrieveItem(extractor.Story.Metadata.URL, image.URL)

                    if not image.CreateFromData(imageData, Configuration.MaximumImageSideLength):

                        imageData = extractor.ExtractMedia(image.URL)

                        if imageData:
                            image.CreateFromData(imageData, Configuration.MaximumImageSideLength)

                    else:

                        retrievedFromCache = True

                    if image:

                        if not retrievedFromCache:
                            self._cache.AddItem(
                                extractor.Story.Metadata.URL,
                                image.URL,
                                image.Data
                            )

                        self._interface.ProgressBar(
                            index,
                            imageCount,
                            Configuration.ProgressBarLength,
                            f"# Downloaded image {index}/{imageCount}",
                            True
                        )

                        if imageCount == index:
                            print()

                        downloadedImageCount += 1
                        previousImageFailedToDownload = False

                    else:

                        if (index > 1) and (not previousImageFailedToDownload):
                            print()

                        self._interface.Error(
                            f'Failed to download image {index}/{imageCount}: "{image.URL}".'
                        )

                        previousImageFailedToDownload = True

                self._interface.Comment(
                    f"Successfully downloaded {downloadedImageCount}/{imageCount} image(s)."
                )

        # Process content.

        self._interface.Process("Processing content...", section = True)

        extractor.Story.Process()

        for index, chapter in enumerate(extractor.Story.Chapters, start = 1):

            # Store original content.

            if self._arguments.Debug:

                fileName = SanitizeFileName(f"{index} - Original.html")
                fileSubdirectoryName = SanitizeFileName(extractor.Story.Metadata.Title)

                WriteTextFile(
                    Configuration.DebugDirectoryPath / fileSubdirectoryName / fileName,
                    chapter.Content
                )

            # The sanitizer is used twice - once before any other processing, once after every other
            # processor. The first time is required to clean up the story (remove empty tags and tag
            # trees, for example), the second to guarantee that the story is actually sanitized.

            chapter.Content = SanitizerProcessor().Process(chapter.Content)
            chapter.Content = TypographyProcessor().Process(chapter.Content)
            chapter.Content = SanitizerProcessor().Process(chapter.Content)

            # Store processed content.

            if self._arguments.Debug:

                fileName = SanitizeFileName(f"{index} - Processed.html")
                fileSubdirectoryName = SanitizeFileName(extractor.Story.Metadata.Title)

                WriteTextFile(
                    Configuration.DebugDirectoryPath / fileSubdirectoryName / fileName,
                    chapter.Content
                )

        if not extractor.Story.Metadata.WordCount:
            extractor.Story.Metadata.WordCount = extractor.Story.CalculateWordCount()

        self._interface.Comment("Content processed.")

        # Format and save the story.

        self._interface.Process("Formatting and saving the story...", section = True)

        # Create the output directory.

        outputFilePaths = self._GetOutputFilePaths(
            self._arguments.Output,
            extractor.Story
        )

        outputFilePaths["Directory"].mkdir(parents = True, exist_ok = True)

        # Format and save the story to HTML.

        if not outputFilePaths["HTML"].is_file():

            if not FormatterHTML(self._arguments.Images).FormatAndSave(
                extractor.Story,
                outputFilePaths["HTML"]
            ):
                logging.error("Failed to format the story as HTML.")

        # Format and save the story to ODT.

        if not outputFilePaths["ODT"].is_file():

            if not FormatterODT(self._arguments.Images).FormatAndSave(
                extractor.Story,
                outputFilePaths["ODT"]
            ):
                logging.error("Failed to format the story as ODT.")

        # Format and save the story to PDF.

        coverImageData = None

        if (not outputFilePaths["PDF"].is_file()) and self._arguments.LibreOffice.is_file():

            if not FormatterPDF(self._arguments.Images).ConvertFromODT(
                outputFilePaths["ODT"],
                outputFilePaths["PDF"].parent,
                self._arguments.LibreOffice
            ):
                logging.error("Failed to format the story as PDF.")

        if outputFilePaths["PDF"].is_file():
            coverImageData = RenderPageToBytes(outputFilePaths["PDF"], 0)

        # Format and save the story to EPUB.

        if not outputFilePaths["EPUB"].is_file():

            if not FormatterEPUB(self._arguments.Images, coverImageData).FormatAndSave(
                extractor.Story,
                outputFilePaths["EPUB"]
            ):
                logging.error("Failed to format the story as EPUB.")

        # Format and save the story to MOBI.

        if (not outputFilePaths["MOBI"].is_file()) and FindEbookConvert():

            if not FormatterMOBI(self._arguments.Images).ConvertFromEPUB(
                outputFilePaths["EPUB"],
                outputFilePaths["MOBI"].parent
            ):
                logging.error("Failed to format the story as MOBI.")

        # Notify the user.

        self._interface.Comment("Story saved successfully!")

        return True

    def _PrintMetadata(self, story: Story) -> None:

        ##
        #
        # Prints a story's metadata.
        #
        # @param story The story.
        #
        ##

        prettifiedMetadata = story.Metadata.GetPrettified()

        data = [
            ["Title:", self._GetPrintableStoryTitle(story)],
            ["Author:", prettifiedMetadata.Author],
            ["Date published:", prettifiedMetadata.DatePublished],
            ["Date updated:", prettifiedMetadata.DateUpdated],
            ["Chapter count:", prettifiedMetadata.ChapterCount],
            ["Word count:", prettifiedMetadata.WordCount],
        ]

        termtables.print(
            data,
            style = termtables.styles.thin,
            padding = (0, 1),
            alignment = "rl"
        )

    def _GetOutputFilePaths(self, outputPath: str, story: Story) -> Dict:

        ##
        #
        # Generates file paths for output files.
        #
        # @param outputPath Directory in which all the application's output is placed.
        # @param story      The story.
        #
        # @return A dictionary: keys correspond to formats, values to file paths.
        #
        ##

        prettifiedMetadata = story.Metadata.GetPrettified()

        sanitizedStoryTitle = self._GetPrintableStoryTitle(story)
        sanitizedAuthor = SanitizeFileName(prettifiedMetadata.Author)

        outputDirectoryPath = \
            Path(expandvars(outputPath)) / sanitizedAuthor / sanitizedStoryTitle

        return {
            "Directory": outputDirectoryPath,
            "HTML": outputDirectoryPath / (sanitizedStoryTitle + ".html"),
            "ODT" : outputDirectoryPath / (sanitizedStoryTitle + ".odt" ),
            "PDF" : outputDirectoryPath / (sanitizedStoryTitle + ".pdf" ),
            "EPUB": outputDirectoryPath / (sanitizedStoryTitle + ".epub"),
            "MOBI": outputDirectoryPath / (sanitizedStoryTitle + ".mobi"),
        }

    def _GetPrintableStoryTitle(self, story: Story) -> str:

        prettifiedMetadata = story.Metadata.GetPrettified()

        title = Transliterate(prettifiedMetadata.Title)
        title = SanitizeFileName(title)
        title = re.sub("\s+", " ", title)

        return title

    def _GenerateNotices(self) -> List[str]:

        notices = []

        if not FindEbookConvert():
            notices.append(
                "Calibre doesn't seem to be installed on this machine. MOBI output files will not "
                "be generated."
            )

        if not self._arguments.LibreOffice.is_file():
            notices.append(
                "LibreOffice doesn't seem to be installed on this machine. PDF output files will "
                "not be generated."
            )

        return notices