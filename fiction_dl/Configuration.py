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
# Imports
#
#
#

# Standard packages.

from pathlib import Path
import tempfile

#
#
#
# Globals.
#
#
#

ApplicationName = "fiction-dl"
ApplicationVersion = "1.1.1"
ApplicationShortDescription = (
    "A fiction downloader, capable of retrieving works of fiction from the net and saving them in a"
    "few common file formats."
)
ApplicationURL = "https://github.com/DreamCobbler/fiction-dl"

CreatorName = "Benedykt Synakiewicz"
CreatorContact = "dreamcobbler@outlook.com"

UserAgent = f"{ApplicationName} {ApplicationVersion}"

RedditClientID = "ScszEQn1cI7GgQ"
RedditRedirectURI = "http://localhost:8080"

CacheDirectoryPath = tempfile.gettempdir() / Path(f"{ApplicationName} Cache")
DebugDirectoryPath = Path(f"{ApplicationName} Debug Data")
OutputDirectoryPath = Path(f"{ApplicationName} Downloads")
SkippedURLsFilePath = Path(f"{ApplicationName} Skipped URLs.txt")

# Maximum length of the longer side of an embedded image.
MaximumImageSideLength = 800

# The time application waits after downloading a chapter, in seconds.
PostChapterSleepTime = 0.5

# About repeated connection attempts.
MaximumConnectionAttemptCount = 10
ConnectionAttemptWait = 2.0