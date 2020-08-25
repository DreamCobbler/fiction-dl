# [fiction-dl](https://github.com/DreamCobbler/fiction-dl) (*1.5.0 alpha*)

![Screenshot](/Screenshot.png?raw=true)

**fiction-dl** is a command-line utility used for downloading works of fiction from the web, formatting them and storing them in a few common file formats. It requires a [Python](https://www.python.org/) interpreter installed, version 3.8 or higher.

I've created it mostly as an exercise in Python - the good old [FanFicFare](https://github.com/JimmXinu/FanFicFare) serves the same purpose and has a much longer list of supported sites. It can also *update* already downloaded stories, not to mention that it can be used as a [Calibre](https://calibre-ebook.com/) plug-in just as well as a command-line tool! But with all that said, **fiction-dl** *does* have some adventages over FFF:

- It supports some sites FFF doesn't (Reddit).
- It can generate ODT and PDF files.
- It applies some typographic corrections to downloaded texts.
- It has much more verbose output.

## Features

### Downloading stories

**fiction-dl** can download stories from a multitude of sites - it some cases it also supports downloading all stories published by a specific user (downloading stories from a *channel*).

| Category         | Site                                                              | Authentication support | Channel support |
|------------------|-------------------------------------------------------------------|------------------------|-----------------|
| fanfiction       | [Archive of Our Own](https://archiveofourown.org/)                | ✗ no                   | ✓ **yes**       |
| fanfiction       | [FanFiction.net](https://www.fanfiction.net/)                     | ✗ no                   | ✓ **yes**       |
| fanfiction       | [SpaceBattles.com](https://forums.spacebattles.com/)              | ✓ **yes**              | ✗ no            |
| fanfiction       | [SufficientVelocity.com](https://forums.sufficientvelocity.com/)  | ✓ **yes**              | ✗ no            |
| fanfiction       | [AlternateHistory.com](https://www.alternatehistory.com/forum/)   | ✓ **yes**              | ✗ no            |
| original fiction | [Fiction Press](https://www.fictionpress.com/)                    | ✗ no                   | ✓ **yes**       |
| original fiction | [Reddit](https://www.reddit.com/)                                 | ✓ **yes**              | ✗ no            |
| erotica          | [AdultFanFiction](http://www.adult-fanfiction.org/html-index.php) | ✗ no                   | ✗ no            |
| erotica          | [Literotica](https://www.literotica.com/)                         | ✗ no                   | ✗ **yes**       |

It is also capable of reading stories saved in text files. You can put the HTML-formatted story in a raw text file and use **fiction-dl** to auto-format it as ODT, PDF etc.

### Formatting stories

Downloaded stories are auto-formatted and saved in following file formats:

- [HTML](https://en.wikipedia.org/wiki/HTML) (.html).
- [EPUB](https://en.wikipedia.org/wiki/EPUB) (.epub).
- [OpenDocument](https://en.wikipedia.org/wiki/OpenDocument) (.odt).
- [Portable Document Format](https://en.wikipedia.org/wiki/PDF) (.pdf).

(Creating PDF output files requires [LibreOffice](https://www.libreoffice.org/) installed on the machine.)

### Embedding images

The application can download images found in story content and embed them in output files.

### Typographic corrections

**fiction-dl** can apply basic typographic corrections to the content of downloaded stories. For example:

| Source Text                  | Corrected Text           |
|------------------------------|--------------------------|
| Lorem ipsum... dolor.        | Lorem ipsum… dolor.      |
| Lorem ipsum...dolor.         | Lorem ipsum… dolor.      |
| Lorem ipsum...... dolor.     | Lorem ipsum… dolor.      |
| Lorem ipsum , dolor.         | Lorem ipsum, dolor.      |
| Lorem ipsum????? Dolor.      | Lorem ipsum? Dolor.      |
| Lorem ipsum - dolor.         | Lorem ipsum — dolor.     |

## Installation

You can install **fiction-dl** using *pip*:

    pip install --upgrade fiction-dl

If the package's already installed, this command will also update it.

If you're running a Debian-derived Linux distribution, you might also want to install the following packages:

    apt-get install libgl1-mesa-glx libglib2.0-0 libmupdf-dev

(**fiction-dl** uses OpenCV for processing downloaded images, which requires them to be installed. PyMuPDF requires libmupdf-dev when it's being build from source.)

## Usage

To download a story from a URL, simply type:

    fiction-dl URL

In order to download multiple stories, create a text file and place the URLs in it, each one in a separate line. Then type:

    fiction-dl YourFilesName

**fiction-dl** offers a few options - you can view them using following command:

    fiction-dl -h

### Using the Text File Extractor

Create a text file meant to contain the story. In its first lines type:

    LOCAL TEXT STORY
    *URL*
    *The Title of the Story*
    *The Author*
    *The One-Line Summary*

Follow it by the story's content, wrapped in HTML tags. Then call:

    fiction-dl FilePath.txt

You can insert chapter-breaks in the story by typing "CHAPTER BREAK LINE" in an empty line.

## License

**GNU GPL 3**. The text of the license is provided in the *LICENSE* file.

## Changelogs

### 1.4.0

**Extractors**:

- Added a text file extractor: you can now put the HTML-formatted story in a raw text file and use **fiction-dl** to auto-format it as ODT, PDF etc.

**Processing:**

- Improved chapter title processing.

**Bugfixes:**

- Fixed a bug in the sanitizer.
- Fixed a typo in Xen Foro extractors' authentication screen.

**Stuff:**

- Removed one unneeded dependency (the *fitz* package).
- Updated the readme: mentioned some libraries that might need to be installed on Linux systems.
- Fixed some typos.

### 1.3.0

**Processing:**

- Improved chapter title processing.

**Bugfixes:**

- Fixed a bug in the ODT formatter.
- Fixed a bug in the FF.net extractor.

### 1.2.0

**General:**

- Links (anchors) are now preserved in output files.

**Extractors**:

- Added an extractor for [AdultFanFiction](http://www.adult-fanfiction.org/html-index.php).

**Processing:**

- Improved horizontal line recognition.
- Improved story title processing.

**Stuff:**

- Reformatted *Style Guidelines* as Markdown.
- Reformatted changelogs as Markdown.

### 1.1.1

**Stuff:**

- Fixed a mistake in the readme.

### 1.1.0

**General**:

- Reworked the way authentication works in all extractors.

**Extractors**:

- Added support for Reddit authentication.
- Expanded exception handling in the Reddit extractor.
- The Reddit extractor now handles extracting posts made by deleted users and suspended users.

**Processing**:

- Added some more processing for story titles.

## Technical

### Documentation

You can generate code documentation using [**Doxygen**](https://www.doxygen.nl/index.html); the relevant configuration file is *Docs/Docs.doxygen*. Generated files will appear in the *Docs/Code Documentation* directory.

### Tests

Launching the **Integration Test** can be done by entering the *Tests* directory and executing the following code:

    python "Integration Test"

In order to launch **unit tests**, enter the *Tests* directory and execute:

    python "Unit Tests.py"