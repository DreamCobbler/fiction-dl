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

import fiction_dl.Configuration as Configuration

# Standard packages.

from typing import Optional

# Non-standard packages.

import colorama
from termcolor import colored

#
#
#
# Classes.
#
#
#

##
#
# Represents the textual user interface.
#
##

class Interface:

    def __init__(self):

        colorama.init()

    def Text(
        self,
        text: str,
        section: bool = False,
        clearLine: bool = False,
        end: str = "\n",
        color: Optional[str] = None,
        bold: bool = False
    ) -> None:

        ##
        #
        # Prints a text.
        #
        # @param text The content.
        #
        ##

        if section:
            print()

        if clearLine:
            print("\r", end = "")

        attributes = ["bold"] if bold else []

        if color:
            text = colored(text, color = color, attrs = attributes)
        elif bold:
            text = colored(text, attrs = attributes)

        print(text, end = end)

    def Comment(
        self,
        text: str,
        section: bool = False,
        clearLine: bool = False,
        end: str = "\n"
    ) -> None:

        ##
        #
        # Prints a comment.
        #
        # @param text The content.
        #
        ##

        self.Text("# " + text, section, clearLine, end)

    def Process(
        self,
        text: str,
        section: bool = False,
        clearLine: bool = False,
        end: str = "\n"
    ) -> None:

        ##
        #
        # Prints a process.
        #
        # @param text The content.
        #
        ##

        self.Text("> " + text, section, clearLine, end, color = "cyan", bold = True)

    def Error(
        self,
        text: str,
        section: bool = False,
        clearLine: bool = False,
        end: str = "\n"
    ) -> None:

        ##
        #
        # Prints a process.
        #
        # @param text The content.
        #
        ##

        self.Text("! " + text, section, clearLine, end, color = "red")

    def EmptyLine(self) -> None:

        ##
        #
        # Prints an empty line.
        #
        ##

        print()

    def LineBreak(self) -> None:

        ##
        #
        # Prints a line break.
        #
        ##

        self.Text(
            Configuration.LineBreak,
            section = True,
            color = "cyan"
        )
