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

# Standard packages.

from pathlib import Path
from shutil import rmtree
from typing import Any

# Non-standard packages.

from bs4 import BeautifulSoup
from dreamy_utilities.Filesystem import GetUniqueFileName, ReadTextFile, WriteTextFile
from dreamy_utilities.Text import Bytify

#
#
#
# Classes.
#
#
#

##
#
# Represents the application's cache.
#
##

class Cache:

    def __init__(self, directoryPath: Path) -> None:

        ##
        #
        # The constructor.
        #
        # @param directoryPath The path of the cache's directory. It will be created if necessary.
        #                      Needs to be write-able.
        #
        ##

        self._directoryPath = directoryPath
        self._items = {}

        # Create the directory and attempt to read pre-existing cache.

        self._directoryPath.mkdir(parents = True, exist_ok = True)
        self._ReadIndexFromFile()

    def AddItem(self, owner: str, name: str, data: Any) -> None:

        ##
        #
        # Adds an item to the cache.
        #
        # @param owner The namespace.
        # @param name  The name of the item.
        # @param data  Data to be stored.
        #
        ##

        if (not owner) or (not name) or (not data):
            return

        if self.ContainsItem(owner, name):
            Path(self._items[owner][name]).unlink()

        filePath = self._directoryPath / GetUniqueFileName()
        with open(filePath, "wb") as file:
            file.write(Bytify(data))

        self._items.setdefault(owner, {})
        self._items[owner][name] = filePath

        self._SaveIndexToFile()

    def RetrieveItem(self, owner: str, name: str) -> bytes:

        ##
        #
        # Reads an item from the cache.
        #
        # @param owner The namespace.
        # @param item  The name of the item.
        #
        # @return The data associated with the item.
        #
        ##

        if (owner not in self._items) or (name not in self._items[owner]):
            return None

        with open(self._items[owner][name], "rb") as file:
            return file.read()

    def ContainsItem(self, owner: str, name: str) -> bool:

        ##
        #
        # Checks whether the cache contains given item.
        #
        # @param owner The namespace.
        # @param item  The name of the item.
        #
        # @return **True** if the item is present in the cache, **False** otherwise.
        #
        ##

        return (owner in self._items) and (name in self._items[owner])

    def Clear(self) -> None:

        ##
        #
        # Clears the cache.
        #
        ##

        self._items.clear()

        rmtree(self._directoryPath)
        self._directoryPath.mkdir(parents = True, exist_ok = True)

    def _ReadIndexFromFile(self) -> None:

        ##
        #
        # Reads the contents of the cache from the index file.
        #
        ##

        code = ReadTextFile(self._directoryPath / self._IndexFileName)
        if not code:
            return

        soup = BeautifulSoup(code, "xml")

        indexNode = soup.find("Index")
        if not indexNode:
            return

        for ownerNode in indexNode.find_all(recursive = False):

            ownerName = ownerNode.find("Name").get_text()
            self._items[ownerName] = {}

            for itemNode in ownerNode.find("Items").find_all(recursive = False):

                itemName = itemNode.find("Name").get_text()
                itemValue = itemNode.find("Value").get_text()

                self._items[ownerName][itemName] = itemValue

    def _SaveIndexToFile(self) -> None:

        ##
        #
        # Saves the index to the index file.
        #
        ##

        soup = BeautifulSoup(features = "xml")

        indexNode = soup.new_tag("Index")
        soup.append(indexNode)

        for ownerName, itemDictionary in self._items.items():

            ownerNode = soup.new_tag("Owner")
            indexNode.append(ownerNode)

            ownerNameNode = soup.new_tag("Name")
            ownerNameNode.string = ownerName
            ownerNode.append(ownerNameNode)

            ownerItemsNode = soup.new_tag("Items")
            ownerNode.append(ownerItemsNode)

            for name, value in itemDictionary.items():

                itemNode = soup.new_tag("Item")
                ownerItemsNode.append(itemNode)

                nameNode = soup.new_tag("Name")
                nameNode.string = name
                itemNode.append(nameNode)

                valueNode = soup.new_tag("Value")
                valueNode.string = str(value)
                itemNode.append(valueNode)

        WriteTextFile(self._directoryPath / self._IndexFileName, str(soup))

    _IndexFileName = "Index.xml"