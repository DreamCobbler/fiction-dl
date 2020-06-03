# [fiction-dl](https://github.com/DreamCobbler/fiction-dl) (*1.2.0 Alpha*)

**(Current stable release is 1.1.1 - you can find it in the [Releases tab](https://github.com/DreamCobbler/fiction-dl/releases) on GitHub.)**

**fiction-dl** is a command-line utility used for downloading works of fiction from the web, formatting them and storing them in a few common file formats. It requires a [Python](https://www.python.org/) interpreter installed, version 3.8 or higher.

I've created it mostly as an exercise in Python - the good old [FanFicFare](https://github.com/JimmXinu/FanFicFare) serves the same purpose and has a much longer list of supported sites. It can also *update* already downloaded stories, not to mention that it can be used as a [Calibre](https://calibre-ebook.com/) plug-in just as well as a command-line tool! But with all that said, **fiction-dl** *does* have some adventages over FFF:

- It supports some sites FFF doesn't (Reddit).
- It can generate ODT and PDF files.
- It applies some typographic corrections to downloaded texts.
- It has much more verbose output.

## Features

### Downloading stories

**fiction-dl** is capable of downloading stories from following sites:

##### Fanfiction

- [Archive of Our Own](https://archiveofourown.org/).
- [FanFiction.net](https://www.fanfiction.net/).
- [SpaceBattles.com](https://forums.spacebattles.com/). (Supports user authentication.)
- [SufficientVelocity.com](https://forums.sufficientvelocity.com/). (Supports user authentication.)
- [AlternateHistory.com](https://www.alternatehistory.com/forum/). (Supports user authentication.)

##### Original Fiction

- [Fiction Press](https://www.fictionpress.com/).
- [Reddit](https://www.reddit.com/). (Supports user authentication.)

##### Erotica

- [Literotica](https://www.literotica.com/).

### Formatting stories

Downloaded stories can be saved in following file formats:

- [HTML](https://en.wikipedia.org/wiki/HTML) (.html).
- [EPUB](https://en.wikipedia.org/wiki/EPUB) (.epub).
- [OpenDocument](https://en.wikipedia.org/wiki/OpenDocument) (.odt).
- [Portable Document Format](https://en.wikipedia.org/wiki/PDF) (.pdf).

(Creating PDF output files requires [LibreOffice](https://www.libreoffice.org/) installed on the machine.)

### Embedding images

The application can download images found in story content and embed them in output files.

### Typographic corrections

**fiction-dl** can apply basic typographic corrections to the content of downloaded stories.

## Installation

You can install **fiction-dl** using *pip*:

    pip install --upgrade fiction-dl

(If the package's already installed, this command will also update it.)

## Usage

To download a story from a URL, simply type:

    fiction-dl URL

In order to download multiple stories, create a text file and place the URLs in it, each one in a separate line. Then type:

    fiction-dl YourFilesName

**fiction-dl** offers a few options - you can view them using following command:

    fiction-dl -h

## License

**GNU GPL 3**. The text of the license is provided in the *Docs/License.txt* file.

## Changelog

All changelogs can be found in the *Docs/Changelogs* directory.

## Technical

### Documentation

You can generate code documentation using [**Doxygen**](https://www.doxygen.nl/index.html); the relevant configuration file is *Docs/Docs.doxygen*. Generated files will appear in the *Docs/Code Documentation* directory.

### Tests

Launching the **Integration Test** can be done by entering the *Tests* directory and executing the following code:

    python "Integration Test"

In order to launch **unit tests**, enter the *Tests* directory and execute:

    python "Unit Tests.py"