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

from fiction_dl.Concepts.Extractor import Extractor
from fiction_dl.Extractors.ExtractorAdultFanfiction import ExtractorAdultFanfiction
from fiction_dl.Extractors.ExtractorAH import ExtractorAH
from fiction_dl.Extractors.ExtractorAO3 import ExtractorAO3
from fiction_dl.Extractors.ExtractorAsstrKristen import ExtractorAsstrKristen
from fiction_dl.Extractors.ExtractorFFNet import ExtractorFFNet
from fiction_dl.Extractors.ExtractorFicWad import ExtractorFicWad
from fiction_dl.Extractors.ExtractorHentaiFoundry import ExtractorHentaiFoundry
from fiction_dl.Extractors.ExtractorHPFF import ExtractorHPFF
from fiction_dl.Extractors.ExtractorLiterotica import ExtractorLiterotica
from fiction_dl.Extractors.ExtractorNajlepszaErotyka import ExtractorNajlepszaErotyka
from fiction_dl.Extractors.ExtractorNifty import ExtractorNifty
from fiction_dl.Extractors.ExtractorQuestionableQuesting import ExtractorQuestionableQuesting
from fiction_dl.Extractors.ExtractorQuotev import ExtractorQuotev
from fiction_dl.Extractors.ExtractorRalst import ExtractorRalst
from fiction_dl.Extractors.ExtractorReddit import ExtractorReddit
from fiction_dl.Extractors.ExtractorSamAndJack import ExtractorSamAndJack
from fiction_dl.Extractors.ExtractorSpaceBattles import ExtractorSpaceBattles
from fiction_dl.Extractors.ExtractorSufficientVelocity import ExtractorSufficientVelocity
from fiction_dl.Extractors.ExtractorTextFile import ExtractorTextFile
from fiction_dl.Extractors.ExtractorWhoFic import ExtractorWhoFic
from fiction_dl.Extractors.ExtractorWuxiaWorld import ExtractorWuxiaWorld

# Standard packages.

from typing import Optional

#
#
#
# Functions.
#
#
#

def CreateExtractor(URL: str) -> Optional[Extractor]:

    ##
    #
    # Creates the appropriate extractor for any given URL.
    #
    # @param URL The URL.
    #
    # @return An initialized extractor object, or **None** if no valid extractor has been found.
    #
    ##

    availableExtractors = [

        ExtractorAdultFanfiction(),
        ExtractorAH(),
        ExtractorAO3(),
        ExtractorAsstrKristen(),
        ExtractorFFNet(),
        ExtractorFicWad(),
        ExtractorHentaiFoundry(),
        ExtractorHPFF(),
        ExtractorLiterotica(),
        ExtractorNajlepszaErotyka(),
        ExtractorNifty(),
        ExtractorQuestionableQuesting(),
        ExtractorQuotev(),
        ExtractorRalst(),
        ExtractorReddit(),
        ExtractorSamAndJack(),
        ExtractorSpaceBattles(),
        ExtractorSufficientVelocity(),
        ExtractorWhoFic(),
        ExtractorWuxiaWorld(),

        ExtractorTextFile(),

    ]

    for extractor in availableExtractors:

        if extractor.Initialize(URL):
            return extractor

    return None