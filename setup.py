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

###
#
#
# Imports.
#
#
###

# Application.

from fiction_dl.Utilities.Filesystem import ReadTextFile
import fiction_dl.Configuration as Configuration

# Standard packages.

from setuptools import find_packages, setup

###
#
#
# The start-up routine.
#
#
###

setup(

    name = Configuration.ApplicationName,
    version = Configuration.ApplicationVersion,

    author = Configuration.CreatorName,
    author_email = Configuration.CreatorContact,

    description = Configuration.ApplicationShortDescription,
    long_description = ReadTextFile("README.md"),
    long_description_content_type = "text/markdown",

    url = Configuration.ApplicationURL,

    install_requires = [

        "bs4",
        "bleach",
        "html5lib",
        "lxml",

        "babel",
        "titlecase",

        "opencv-python",
        "numpy",

        "fitz",
        "PyMuPDF",

        "markdown",
        "praw",

        "pyopenssl",
        "tldextract",

        "ebooklib",

    ],

    packages = find_packages(),
    package_data = {

        "": [
            "*.css",
            "*.html",
            "*.odt",
            "*.xml"
        ]

    },

    entry_points = {

        "console_scripts": [
            "fiction-dl = fiction_dl.__main__:Main"
        ]

    },

    classifiers = [

        # Development Status :: 1 - Planning
        # Development Status :: 2 - Pre-Alpha
        # Development Status :: 3 - Alpha
        # Development Status :: 4 - Beta
        # Development Status :: 5 - Production/Stable
        # Development Status :: 6 - Mature
        # Development Status :: 7 - Inactive
        "Development Status :: 5 - Production/Stable",

        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",

        "Operating System :: OS Independent",
        "Environment :: Console",

        "Intended Audience :: End Users/Desktop",
        "Topic :: Internet :: WWW/HTTP",

    ],

    python_requires = ">=3.8",

)