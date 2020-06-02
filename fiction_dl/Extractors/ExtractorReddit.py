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
from fiction_dl.Concepts.Extractor import Extractor
from fiction_dl.Utilities.General import GetDateFromTimestamp
from fiction_dl.Utilities.Text import GetLevenshteinDistance
import fiction_dl.Configuration as Configuration

# Standard packages.

import logging
import re
from typing import List, Optional

# Non-standard packages.

from markdown import markdown
from praw import Reddit
from praw.exceptions import InvalidURL
from praw.models import Submission
from prawcore.exceptions import Forbidden, NotFound

#
#
#
# The class definition.
#
#
#

class ExtractorReddit(Extractor):

    @staticmethod
    def SupportsAuthentication() -> bool:

        return False

    def __init__(self) -> None:

        ##
        #
        # The constructor.
        #
        ##

        super().__init__()

        self._redditInstance = Reddit(
            client_id = Configuration.RedditClientID,
            client_secret = "",
            redirect_uri = "",
            user_agent = Configuration.UserAgent
        )

    def GetSupportedHostnames(self) -> List[str]:

        ##
        #
        # Returns a list of hostnames supposed to be supported by the extractor.
        #
        # @return A list of supported hostnames.
        #
        ##

        return [
            "reddit.com"
        ]

    def SupportsAuthentication(self) -> bool:

        ##
        #
        # Checks whether the extractor supports user authentication.
        #
        # @return **True** if the site *does* support authentication, **False** otherwise.
        #
        ##

        return False

    def Authenticate(self, username: str, password: str) -> bool:

        ##
        #
        # Logs the user in, using provided data.
        #
        # @param username The username.
        # @param password The password.
        #
        # @return **True** if the user has been authenticated correctly, **False** otherwise.
        #
        ##

        return False

    def Scan(self) -> bool:

        ##
        #
        # Scans the story: generates the list of chapter URLs and retrieves the
        # metadata.
        #
        # @return **False** when the scan fails, **True** when it doesn't fail.
        #
        ##

        try:

            if not self.Story:
                logging.error("The extractor isn't initialized.")
                return False

            # Retrieve chapter URLs.

            try:

                submission = Submission(self._redditInstance, url = self.Story.Metadata.URL)

                storyTitleProper = self._GetTitleProper(submission.title)
                if not storyTitleProper:
                    logging.error("Failed to read story title.")
                    return False

            except Forbidden:

                logging.error("PRAW says: Forbidden.")
                return False

            except InvalidURL:

                logging.error("PRAW says: InvalidURL.")
                return False

            except NotFound:

                logging.error("PRAW says: Forbidden.")
                return False

            if submission.author:

                try:

                    for nextSubmission in submission.author.submissions.new():

                        if submission.subreddit.display_name != nextSubmission.subreddit.display_name:
                            continue

                        titleProper = self._GetTitleProper(nextSubmission.title)
                        if not titleProper:
                            continue

                        distance = GetLevenshteinDistance(storyTitleProper, titleProper)
                        if distance > 5:
                            continue

                    self._chapterURLs.append(nextSubmission.url)

                except (NotFound, InvalidURL, Forbidden):

                    pass

                self._chapterURLs.reverse()

            if not self._chapterURLs:
                self._chapterURLs = [submission.url]

            # Extract metadata.

            firstSubmission = Submission(self._redditInstance, url = self._chapterURLs[0])
            lastSubmission = Submission(self._redditInstance, url = self._chapterURLs[-1])

            storyTitleProper = self._GetTitleProper(firstSubmission.title)

            self.Story.Metadata.Title = storyTitleProper
            self.Story.Metadata.Author = (
                firstSubmission.author.name
                if firstSubmission.author else
                "[deleted]"
            )
            self.Story.Metadata.DatePublished = GetDateFromTimestamp(int(firstSubmission.created_utc))
            self.Story.Metadata.DateUpdated = GetDateFromTimestamp(int(lastSubmission.created_utc))
            self.Story.Metadata.ChapterCount = len(self._chapterURLs)
            self.Story.Metadata.WordCount = 0
            self.Story.Metadata.Summary = "No summary."

            # Return.

            return True

        except Forbidden:

            logging.error("PRAW says: Forbidden.")
            return False

        except InvalidURL:

            logging.error("PRAW says: InvalidURL.")
            return False

        except NotFound:

            logging.error("PRAW says: Forbidden.")
            return False

    def ExtractChapter(self, index: int) -> Optional[Chapter]:

        ##
        #
        # Extracts specific chapter.
        #
        # @param index The index of the chapter to be extracted.
        #
        # @return **True** if the chapter is extracted correctly, **False** otherwise.
        #
        ##

        if index > len(self._chapterURLs):
            logging.error(
                f"Trying to extract chapter {index}. "
                f"Only {len(self._chapterURLs)} chapter(s) located. "
                f"The story supposedly has {self.Story.Metadata.ChapterCount} chapter(s)."
            )
            return None

        submission = Submission(self._redditInstance, url = self._chapterURLs[index - 1])

        return Chapter(content = markdown(submission.selftext))

    @staticmethod
    def _GetTitleProper(title: str) -> Optional[str]:

        ##
        #
        # Retrieves the proper title of the story (removing parts like "(Part 6)" or "[Chapter 2]").
        #
        # @param title The title as it was retrieved from Reddit.
        #
        # @return The title proper.
        #
        ##

        if not title:
            return None

        titleProper = title

        titleProper = re.sub("\[?\(?Finale\)?\]?\.?", "", titleProper)
        titleProper = re.sub("\[?\(?Final part\)?\]?\.?", "", titleProper)
        titleProper = re.sub("\[?\(?Final update\)?\]?\.?", "", titleProper)
        titleProper = re.sub("\[?\(?Final\)?\]?\.?", "", titleProper)
        titleProper = re.sub("\[?\(?Part (\d+)\)?\]?\.?", "", titleProper)
        titleProper = re.sub("\[?\(?Update (\d+)\)?\]?\.?", "", titleProper)

        titleProper = titleProper.strip()

        return titleProper.strip()