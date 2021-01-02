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

# If the script is run by filename, add the current directory to PATH. This is necessary to make all
# the imports work (otherwise "fiction_dl." would lead nowhere).

if __package__ is None:

    try:

        from Utilities.Filesystem import GetPackageDirectory

    except ImportError:

        from fiction_dl.Utilities.Filesystem import GetPackageDirectory

    from dreamy_utilities.Filesystem import AddToPATH

    AddToPATH(GetPackageDirectory().parent)

# Application.

from fiction_dl.Core.Application import Application
from fiction_dl.Utilities.Filesystem import GetLibreOfficeExecutablePath
import fiction_dl.Configuration as Configuration

# Standard packages.

from argparse import ArgumentParser, Namespace
from http.client import RemoteDisconnected
import logging
from pathlib import Path
from requests.exceptions import ConnectionError
from sys import exit
from urllib3.exceptions import ProtocolError

#
#
#
# Functions.
#
#
#

def Main() -> None:

    ##
    #
    # The "Main" function of the application.
    #
    ##

    # Read command-line arguments.

    arguments = ReadCommandLineArguments()

    # Set up the logger.

    logging.basicConfig(level = logging.INFO if arguments.Verbose else logging.ERROR)

    # Create and launch the application.

    try:

        Application(
            arguments = arguments,
            cacheDirectoryPath = Configuration.CacheDirectoryPath
        ).Launch()

    except (ConnectionError, ProtocolError, RemoteDisconnected):

        print()
        print("# A connection error has occurred.")

        exit()

def ReadCommandLineArguments() -> Namespace:

    ##
    #
    # Reads the command-line arguments.
    #
    # @return The command-line arguments.
    #
    ##

    epilogMessage =                                                                                              \
        "You can use the application to auto-format a story saved in a text file.\r\n"                           \
        "\r\n"                                                                                                   \
        f"Put the text \"{Configuration.TextSourceFileMagicText}\" in the very first line of the file, then\r\n" \
        "the story's original URL in the next one, then the title in the third one,\r\n"                         \
        "then the author's name in the fourth, the one line summary in the fifth.\r\n"                           \
        "\r\n"                                                                                                   \
        "Then put the HTML-formatted story content in the line after that."                                      \
        "\r\n"                                                                                                   \
        f"You can put \"{Configuration.TextSourceFileChapterBreak}\" in a line in order to force a chapter break."

    argumentParser = ArgumentParser(
        description = Configuration.ApplicationShortDescription,
        epilog = epilogMessage
    )

    argumentParser.add_argument(
        "-a",
        dest = "Authenticate",
        action = "store_true",
        help = "authenticates the user to supported sites using interactive mode"
    )

    argumentParser.add_argument(
        "-c",
        dest = "ClearCache",
        action = "store_true",
        help = "clears the cache before launching the application"
    )

    argumentParser.add_argument(
        "-pack",
        dest = "Pack",
        action = "store_true",
        help = "packs all downloaded stories inside one file (of each type)"
    )

    argumentParser.add_argument(
        "-v",
        dest = "Verbose",
        action = "store_true",
        help = "enables the (more) verbose mode"
    )

    argumentParser.add_argument(
        "-f",
        dest = "Force",
        action = "store_true",
        help = "overwrites output files (in case they already exist)"
    )

    argumentParser.add_argument(
        "-d",
        dest = "Debug",
        action = "store_true",
        help = "enables debug mode (saves some data useful for debugging)"
    )

    argumentParser.add_argument(
        "-no-images",
        dest = "Images",
        action = "store_false",
        help = "disables downloading images found in story content"
    )

    argumentParser.add_argument(
        "-persistent-cache",
        dest = "PersistentCache",
        action = "store_true",
        help = "preserves the cache after the application quits"
    )

    argumentParser.add_argument(
        "-lo",
        dest = "LibreOffice",
        type = Path,
        default = GetLibreOfficeExecutablePath() or Path(),
        help = "path to the LibreOffice executable (soffice.exe)"
    )

    argumentParser.add_argument(
        "-o",
        dest = "Output",
        type = str,
        default = Configuration.OutputDirectoryPath,
        help = "output directory path"
    )

    argumentParser.add_argument(
        "Input",
        type = str,
        help = "a URL, or a path to a text file with one URL per line"
    )

    return argumentParser.parse_args()

#
#
#
# The start-up routine.
#
#
#

if "__main__" == __name__:

    Main()
