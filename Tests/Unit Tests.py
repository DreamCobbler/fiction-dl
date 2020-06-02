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

# Add the fiction_dl package to PATH.

import sys

sys.path.insert(0, "../")

# Application.

from fiction_dl.Utilities.Text import IsStringTrulyEmpty, Truncate
from fiction_dl.Utilities.Web import GetHostname, GetSiteURL

# Standard packages.

import unittest

#
#
#
# Tests.
#
#
#

class TestUtilitiesText(unittest.TestCase):

    def test_IsStringTrulyEmpty(self):

        self.assertIs(
            IsStringTrulyEmpty(None),
            True
        )

        self.assertIs(
            IsStringTrulyEmpty(""),
            True
        )

        self.assertIs(
            IsStringTrulyEmpty("   "),
            True
        )

        self.assertIs(
            IsStringTrulyEmpty("\t\t\t"),
            True
        )

        self.assertIs(
            IsStringTrulyEmpty("   d  "),
            False
        )

    def test_Truncate(self):

        self.assertEqual(
            Truncate("Lorem ipsum dolor", 10),
            "Lorem ips…"
        )

class TestUtilitiesWeb(unittest.TestCase):

    def test_GetHostname(self):

        self.assertEqual(
            GetHostname("https://m.fanfiction.net"),
            "fanfiction.net"
        )

        self.assertEqual(
            GetHostname("https://www.fanfiction.net/u/10283561/ZebJeb"),
            "fanfiction.net"
        )

        self.assertEqual(
            GetHostname("fanfiction.net/s/8787151/1/Mother-Nature"),
            "fanfiction.net"
        )

    def test_GetSiteURL(self):

        self.assertEqual(
            GetSiteURL("protocol://a.b.com/1/2/3/"),
            "protocol://a.b.com"
        )

#
#
#
# The start-up routine.
#
#
#

unittest.main()

