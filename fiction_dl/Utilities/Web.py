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

from fiction_dl.Utilities.General import Stringify

# Standard packages.

from requests import get, Session
from typing import Optional
from urllib.parse import urlparse

# Non-standard packages.

from bs4 import BeautifulSoup
import tldextract

#
#
#
# Functions.
#
#
#

def DownloadPage(URL: str, session: Optional[Session] = None) -> Optional[str]:

    ##
    #
    # Downloads a webpage and returns it a string.
    #
    # @param URL     The input URL.
    # @param session The requests.Session object to be used for the download.
    #
    # @return The downloaded page. Optionally None.
    #
    ##

    if not URL:
        return None

    response = get(URL) if (not session) else session.get(URL)

    return Stringify(response.content)

def DownloadSoup(
    URL: str,
    session: Optional[Session] = None,
    parser: str = "html.parser"
) -> Optional[BeautifulSoup]:

    ##
    #
    # Downloads a webpage and returns a soup of tags.
    #
    # @param URL     The input URL.
    # @param session The requests.Session object to be used for the download.
    #
    # @return Tag soup.
    #
    ##

    code = DownloadPage(URL, session)
    if not code:
        return None

    return BeautifulSoup(code, parser)

def GetHostname(URL: str) -> str:

    ##
    #
    # Retrieves hostname from a URL ("protocol://a.b.com/1/2/3/" returns "protocol:://b.com").
    #
    # @param URL The input URL.
    #
    # @return The hostname extracted from the input URL. Optionally None.
    #
    ##

    if not URL:
        return URL

    parts = tldextract.extract(URL)
    return f"{parts.domain}.{parts.suffix}"

def GetSiteURL(URL: str) -> str:

    ##
    #
    # Returns the URL to the main site ("protocol://a.b.com/1/2/3/" returns "protocol://a.b.com").
    #
    # @param URL The input URL.
    #
    # @return The URL to the main site. Optionally None.
    #
    ##

    if not URL:
        return URL

    URL = urlparse(URL)

    return f"{URL.scheme}://{URL.netloc}"