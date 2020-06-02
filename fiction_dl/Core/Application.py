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
from fiction_dl.Formatters.FormatterEPUB import FormatterEPUB
from fiction_dl.Formatters.FormatterHTML import FormatterHTML
from fiction_dl.Formatters.FormatterODT import FormatterODT
from fiction_dl.Formatters.FormatterPDF import FormatterPDF
from fiction_dl.Processors.SanitizerProcessor import SanitizerProcessor
from fiction_dl.Processors.TypographyProcessor import TypographyProcessor
from fiction_dl.Utilities.Extractors import CreateExtractor
from fiction_dl.Utilities.Filesystem import SanitizeFileName, WriteTextFile
from fiction_dl.Utilities.General import RemoveDuplicates, RenderPageToBytes, Stringify
from fiction_dl.Utilities.HTML import FindImagesInCode, MakeURLAbsolute
from fiction_dl.Utilities.Text import Truncate
from fiction_dl.Utilities.Web import GetSiteURL
import fiction_dl. Configuration as Configuration

# Standard packages.

from argparse import Namespace
import logging
from os.path import expandvars, isfile
from pathlib import Path
from requests.exceptions import ConnectionError
from time import sleep
from typing import Dict, List
from urllib3.exceptions import ProtocolError

#
#
#
# The "Application" class encapsulates the whole logic of the application.
#
#
#

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

    def Launch(self) -> None:

        ##
        #
        # Launches the application.
        #
        ##

        # Welcome the user.

        print(
            f"{Configuration.ApplicationName} {Configuration.ApplicationVersion},"
            f" by {Configuration.CreatorName} <{Configuration.CreatorContact}>"
        )

        # Clear the cache (optional).

        if self._arguments.ClearCache:
            logging.info("Deleting the cache...")
            self._cache.Clear()

        # Prepare the list of URLs.

        print()
        print("> Creating the list of input URLs...")

        URLs = []

        try:

            # Assume that the Input argument is a path to a text file.

            with open(self._arguments.Input, "r", encoding = "utf-8") as file:
                URLs = self._ReadURLsFromLines(file.readlines())

        except OSError:

            # If it's not a path, then it ought to be a URL.

            URLs = [self._arguments.Input]

        print(f"# The list contains {len(URLs)} item(s).")

        # Process each URL.

        skippedURLs = []

        for index, URL in enumerate(URLs, start = 1):

            print()
            print(79 * "-")

            print()
            print(f'# {index}/{len(URLs)}: "{URL}".')

            if not self._ProcessURL(URL):
                skippedURLs.append(URL)

        print()
        print(79 * "-")

        # Print information about skipped stories.

        if skippedURLs:

            print()

            for URL in skippedURLs:
                print(f'! Failed to download a story from URL: "{URL}".')

            WriteTextFile(Configuration.SkippedURLsFilePath, "\n".join(skippedURLs))

        # Print some final information.

        print()
        print(f"# Successfully retrieved {len(URLs) - len(skippedURLs)}/{len(URLs)} stories.")

        # Clear the cache.

        if not self._arguments.PersistentCache:
            logging.info("Deleting the cache...")
            self._cache.Clear()

    @staticmethod
    def _ReadURLsFromLines(lines: List[str]) -> List[str]:

        ##
        #
        # Creates a list of input URLs from lines of a text file.
        #
        # @param lines List of strings being read lines of a text file.
        #
        # @return List of strings: URLs of the stories to be downloaded.
        #
        ##

        if not lines:
            return lines

        URLs = [x.strip() for x in lines]
        URLs = [x for x in URLs if len(x)] # Ignore empty lines.
        URLs = [x for x in URLs if not x.startswith("#")] # Ignore comments.

        return RemoveDuplicates(URLs)

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

        print()
        print("> Creating the extractor...")

        extractor = CreateExtractor(URL)
        if not extractor:
            logging.error("No matching extractor found.")
            return False

        print(f'# Extractor created: "{type(extractor).__name__}".')

        # Authenticate the user (if supported by the extractor).

        if self._arguments.Authenticate:

            if not extractor.SupportsAuthentication():
                print("# This specific extractor does NOT support authentication.")

            elif not extractor.Authenticate():
                logging.error("Failed attempt to authenticate.")
                return False

            else:
                print("# Authenticated successfully.")

        # Scan the story.

        print()
        print("> Scanning the story...")

        if not extractor.Scan():
            logging.error("Failed to scan the story.")
            return False

        self._PrintMetadata(extractor.Story)

        # Check whether the output files already exist.

        outputFilePaths = self._GetOutputFilePaths(self._arguments.Output, extractor.Story)

        if (not self._arguments.Force) and all(x.is_file() for x in outputFilePaths.values()):
            print()
            print("# Output files already exist; no need to recreate them.")
            return True

        elif self._arguments.Force:
            [x.unlink() for x in outputFilePaths.values() if x.is_file()]

        # Extract content.

        print()
        print("> Extracting content...")

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

            print(
                f"\r# Downloaded chapter {index}/{extractor.Story.Metadata.ChapterCount}.",
                end = ""
            )

            if extractor.Story.Metadata.ChapterCount == index:
                print()

            if not retrievedFromCache:
                sleep(Configuration.PostChapterSleepTime)

        # Locate and download images.

        if self._arguments.Images:

            print()
            print("> Downloading images...")

            # Locate the images.

            for chapter in extractor.Story.Chapters:
                extractor.Story.Images.extend(FindImagesInCode(chapter.Content))

            storySiteURL = GetSiteURL(extractor.Story.Metadata.URL)
            for image in extractor.Story.Images:
                image.URL = MakeURLAbsolute(image.URL, storySiteURL)

            print(f"# Found {len(extractor.Story.Images)} image(s).")

            # Download them.

            if extractor.Story.Images:

                imageCount = len(extractor.Story.Images)
                downloadedImageCount = 0

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

                        print(f"\r# Downloaded image {index}/{imageCount}.", end = "")
                        if imageCount == index:
                            print()

                        downloadedImageCount += 1

                    else:

                        if index > 1:
                            print()

                        print(f'! Failed to download image {index}/{imageCount}: "{image.URL}".')

                print(f"# Successfully downloaded {downloadedImageCount}/{imageCount} image(s).")

        # Process content.

        print()
        print("> Processing content...")

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

        print("# Content processed.")

        # Format and save the story.

        print()
        print("> Formatting and saving the story...")

        # Create the output directory.

        outputDirectoryPath = self._GetStoryOutputDirectoryPath(
            self._arguments.Output,
            extractor.Story
        )

        outputDirectoryPath.mkdir(parents = True, exist_ok = True)

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

        if not outputFilePaths["PDF"].is_file():

            if not self._arguments.LibreOffice.is_file():

                print("! Failed to locate the LibreOffice executable: can't create a PDF file.")

            else:

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

        # Notify the user.

        print("# Story saved successfully!")

        return True

    def _PrintMetadata(self, story: Story) -> None:

        ##
        #
        # Prints story's metadata.
        #
        # @param story The story.
        #
        ##

        prettifiedMetadata = story.Metadata.GetPrettified()

        print(f"# Title: {prettifiedMetadata.Title}")
        print(f"# Author: {prettifiedMetadata.Author}")
        print(f"# Date published: {prettifiedMetadata.DatePublished}")
        print(f"# Date updated: {prettifiedMetadata.DateUpdated}")
        print(f"# Chapter count: {prettifiedMetadata.ChapterCount}")
        print(f"# Word count: {prettifiedMetadata.WordCount}")

    def _GetStoryOutputDirectoryPath(self, outputDirectoryPath: str, story: Story) -> Dict:

        ##
        #
        # Generates the output directory path for a specific story.
        #
        # @param outputDirectoryPath Directory in which all the application's output is placed.
        # @param story               The story.
        #
        # @return The output directory path.
        #
        ##

        sanitizedStoryTitle = SanitizeFileName(story.Metadata.GetPrettified().Title)

        return Path(expandvars(outputDirectoryPath)) / sanitizedStoryTitle

    def _GetOutputFilePaths(self, outputDirectoryPath: str, story: Story) -> Dict:

        ##
        #
        # Generates file names for output files.
        #
        # @param outputDirectoryPath Directory in which all the application's output is placed.
        # @param story               The story.
        #
        # @return A dictionary; keys correspond to formats, values to file paths.
        #
        ##

        outputDirectoryPath = self._GetStoryOutputDirectoryPath(outputDirectoryPath, story)
        sanitizedStoryTitle = SanitizeFileName(story.Metadata.GetPrettified().Title)

        return {

            "HTML": outputDirectoryPath / (sanitizedStoryTitle + ".html"),
            "ODT" : outputDirectoryPath / (sanitizedStoryTitle + ".odt" ),
            "PDF" : outputDirectoryPath / (sanitizedStoryTitle + ".pdf" ),
            "EPUB": outputDirectoryPath / (sanitizedStoryTitle + ".epub"),

        }