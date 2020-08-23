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

from fiction_dl.Concepts.Scanner import Scanner
from fiction_dl.Utilities.Web import DownloadSoup, GetHostname

# Standard packages.

import logging
import re
from typing import List, Optional

#
#
#
# Classes.
#
#
#

##
#
# A scanner dedicated for ArchiveOfOurOwn.org.
#
##

class ScannerAO3(Scanner):

    def Scan(self, URL: str) -> Optional[List[str]]:

        ##
        #
        # Scans the channel: generates the list of story URLs.
        #
        # @return **None** when the scan fails, a list of story URLs when it doesn't fail.
        #
        ##

        if (not URL) or (GetHostname(URL) != "archiveofourown.org"):
            return None

        usernameMatch = re.search("/users/([a-zA-Z0-9]+)/", URL)
        if not usernameMatch:
            return None

        username = usernameMatch.group(1)

        normalizedURL = f"https://archiveofourown.org/users/{username}/"
        worksURL = normalizedURL + "works"

        worksSoup = DownloadSoup(worksURL)
        if not worksSoup:
            return None

        worksPagesURLs = []

        if not (worksPaginationElement := worksSoup.find("ol", {"title": "pagination"})):

            worksPagesURLs.append(worksURL)

        else:

            worksPageButtonElements = worksPaginationElement.find_all("li")
            worksPageCount = len(worksPageButtonElements) - 2
            if worksPageCount < 1:
                logging.error("Invalid number of pages on the Works webpage.")
                return None

            for index in range(1, worksPageCount + 1):
                worksPagesURLs.append(worksURL + f"?page={index}")

        workIDs = []

        for pageURL in worksPagesURLs:

            pageSoup = DownloadSoup(pageURL)
            if not pageSoup:
                logging.error("Failed to download a page of the Works webpage.")
                continue

            workElements = pageSoup.find_all("li", {"class": "work"})

            for workElement in workElements:

                linkElement = workElement.find("a")
                if (not linkElement) or (not linkElement.has_attr("href")):
                    logging.error("Failed to retrieve story URL from the Works webpage.")
                    continue

                storyIDMatch = re.search("/works/(\d+)", linkElement["href"])
                if not storyIDMatch:
                    logging.error("Failed to retrieve story ID from its URL.")
                    continue

                storyID = storyIDMatch.group(1)
                workIDs.append(storyID)

        storyURLs = [f"https://archiveofourown.org/works/{ID}" for ID in workIDs]
        return storyURLs