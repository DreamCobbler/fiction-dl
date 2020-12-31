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

from fiction_dl.Concepts.Chapter import Chapter
from fiction_dl.Concepts.Extractor import Extractor
from fiction_dl.Utilities.Filesystem import GetPackageDirectory
from fiction_dl.Utilities.Text import GetTitleProper
import fiction_dl.Configuration as Configuration

# Standard packages.

import logging
from random import randint
import re
import socket
from typing import List, Optional

# Non-standard packages.

from bs4 import BeautifulSoup
from dreamy_utilities.Filesystem import ReadTextFile
from dreamy_utilities.Interface import Interface
from dreamy_utilities.Text import GetDateFromTimestamp, GetLevenshteinDistance, GetLongestLeadingSubstring, PrettifyTitle
from fake_useragent import UserAgent
from markdown import markdown
from praw import Reddit
from praw.exceptions import InvalidURL
from praw.models import Submission
from prawcore.exceptions import Forbidden, InsufficientScope, NotFound
from time import sleep
import webbrowser

#
#
#
# The class definition.
#
#
#

class ExtractorReddit(Extractor):

    def __init__(self) -> None:

        ##
        #
        # The constructor.
        #
        ##

        super().__init__()

        self._downloadChapterSoupWhenExtracting = False

        self._userAgent = UserAgent().random

        if not ExtractorReddit._RefreshToken:
            self._redditInstance = Reddit(
                client_id = Configuration.RedditClientID,
                client_secret = None,
                redirect_uri = Configuration.RedditRedirectURI,
                user_agent = self._userAgent
            )

        else:
            self._redditInstance = Reddit(
                client_id = Configuration.RedditClientID,
                client_secret = None,
                refresh_token = ExtractorReddit._RefreshToken,
                user_agent = self._userAgent
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

        return True

    def Authenticate(self, interface: Interface) -> bool:

        ##
        #
        # Logs the user in, interactively.
        #
        # @param interface The user interface to be used.
        #
        # @return **True** if the user has been authenticated correctly, **False** otherwise.
        #
        ##

        if not ExtractorReddit._RefreshToken:

            scopes = [
                "identity",
                "read",
                "history",
            ]

            state = str(randint(0, 65000))
            authorizationURL = self._redditInstance.auth.url(scopes, state, "permanent")

            interface.Comment(
                f'You authorization URL is: "{authorizationURL}". {Configuration.ApplicationName}'
                " has just attempted to open it in your web browser - if it has failed, then please"
                " open it manually and confirm granting access to"
                f" {Configuration.ApplicationName}."
            )

            webbrowser.open(authorizationURL, new = 2)
            interface.GrabUserAttention()

            # Receive the connection.

            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("localhost", 8080))
            server.listen(1)

            client = server.accept()[0]
            server.close()

            # Process received data.

            data = client.recv(1024).decode("utf-8")
            responseTemplate = ReadTextFile(GetPackageDirectory() / "Resources" / "PrettyHTMLText.html")
            responseTemplate = responseTemplate.replace("@@@ApplicationName@@@", Configuration.ApplicationName)
            responseTemplate = responseTemplate.replace("@@@ApplicationVersion@@@", Configuration.ApplicationVersion)

            if (" " not in data) or ("?" not in data) or ("&" not in data):
                SendMessage(client, responseTemplate.replace("@@@Content@@@", "Error: invalid response."))
                return self.AuthenticationResult.FAILURE

            parameterTokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
            parameters = {
                key: value
                for (key, value) in [token.split("=") for token in parameterTokens]
            }

            if parameters["state"] != state:
                SendMessage(client, responseTemplate.replace("@@@Content@@@", "Error: invalid state in response."))
                return self.AuthenticationResult.FAILURE

            elif "error" in parameters:
                SendMessage(client, responseTemplate.replace("@@@Content@@@", f'Error: {parameters["error"]}.'))
                return self.AuthenticationResult.FAILURE

            else:
                SendMessage(client, responseTemplate.replace("@@@Content@@@", "Everything went well. 😉"))

            # Authorize.

            ExtractorReddit._RefreshToken = self._redditInstance.auth.authorize(parameters["code"])

        # Re-create the reddit instance and notify the user.

        self._redditInstance = Reddit(
            client_id = Configuration.RedditClientID,
            client_secret = None,
            refresh_token = ExtractorReddit._RefreshToken,
            user_agent = self._userAgent
        )

        print(f'# You are authenticated as "{self._redditInstance.user.me()}".')

        return self.AuthenticationResult.SUCCESS

    def ScanStory(self) -> bool:

        ##
        #
        # Scans the story: generates the list of chapter URLs and retrieves the
        # metadata.
        #
        # @return **False** when the scan fails, **True** when it doesn't fail.
        #
        ##

        try:

            if self.Story is None:
                logging.error("The extractor isn't initialized.")
                return False

            # Retrieve chapter URLs.

            try:

                submission = Submission(self._redditInstance, url = self.Story.Metadata.URL)
                subredditName = submission.subreddit.display_name

                storyTitleProper = GetTitleProper(submission.title)
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

                        if subredditName != nextSubmission.subreddit.display_name:
                            continue

                        titleProper = GetTitleProper(nextSubmission.title)
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

            storyTitleProper = PrettifyTitle(firstSubmission.title, removeContext = True)

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

        except InsufficientScope:

            logging.error("PRAW says: InsufficientScope.")
            return False

        except InvalidURL:

            logging.error("PRAW says: InvalidURL.")
            return False

        except NotFound:

            logging.error("PRAW says: Forbidden.")
            return False

    def _InternallyExtractChapter(
        self,
        URL: str,
        soup: Optional[BeautifulSoup]
    ) -> Optional[Chapter]:

        ##
        #
        # Extracts specific chapter.
        #
        # @param URL  The URL of the page containing the chapter.
        # @param soup The tag soup of the page containing the chapter.
        #
        # @return **True** if the chapter is extracted correctly, **False** otherwise.
        #
        ##

        submission = Submission(self._redditInstance, url = URL)

        return Chapter(content = markdown(submission.selftext))

    _RefreshToken = None

#
#
#
# Functions.
#
#
#

def SendMessage(client: socket.socket, message: str) -> None:

    ##
    #
    # Sends a message to client, then closes the connection.
    #
    # @param client  The client.
    # @param message The message.
    #
    ##

    if (not client) or (not message):
        return

    client.send("HTTP/1.1 200 OK\r\n\r\n{}".format(message).encode("utf-8"))
    client.close()
