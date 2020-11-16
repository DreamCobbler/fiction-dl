# ![Logo](/Stuff/Logo%20(64).png?raw=true) [fiction-dl](https://github.com/DreamCobbler/fiction-dl) (*1.7.0 alpha*)

![Screenshot (Windows 10)](/Stuff/Screenshot%20(Windows%2010).png?raw=true)
![Screenshot (Linux Mint 20)](/Stuff/Screenshot%20(Linux%20Mint%2020).png?raw=true)

**fiction-dl** is a command-line utility made for downloading works of fiction from the web, capable of auto-formatting and saving them in a few common file formats. It requires a [Python](https://www.python.org/) interpreter installed, version 3.8 or higher.

The application supports more than a dozen websites, generates HTML, EPUB, MOBI, ODT and PDF output files, applies typographic corrections to the extracted content and is able to embed downloaded images within it.

## ✿ Table of Contents

1. [Features](#features).
2. [Installation](#installation).
3. [Usage](#usage).
4. [License](#license).
5. [Technical](#technical).

## ✿ Features

### Downloading stories

**fiction-dl** can download stories from a multitude of sites - in some cases, it also supports downloading all stories published by any specific user (which is called downloading stories from a *channel*).

| Category         | Site                                                                | Authentication support | Channel support                |
|------------------|---------------------------------------------------------------------|------------------------|--------------------------------|
| fanfiction       | [Archive of Our Own](https://archiveofourown.org/)                  | ✗ no                   | ✓ **yes <sup>[1]</sup>**       |
| fanfiction       | [FanFiction.net](https://www.fanfiction.net/)                       | ✗ no                   | ✓ **yes**                      |
| fanfiction       | [FicWad.com](https://ficwad.com/)                                   | ✗ no                   | ✓ **yes**                      |
| fanfiction       | [SpaceBattles.com](https://forums.spacebattles.com/)                | ✓ **yes**              | ✗ no                           |
| fanfiction       | [SufficientVelocity.com](https://forums.sufficientvelocity.com/)    | ✓ **yes**              | ✗ no                           |
| fanfiction       | [AlternateHistory.com](https://www.alternatehistory.com/forum/)     | ✓ **yes**              | ✗ no                           |
| fanfiction       | [QuestionableQuesting.com](https://forum.questionablequesting.com/) | ✗ no                   | ✗ no                           |
| fanfiction       | [HarryPotterFanFiction.com](https://harrypotterfanfiction.com/)     | ✗ no                   | ✗ no                           |
| original fiction | [Fiction Press](https://www.fictionpress.com/)                      | ✗ no                   | ✓ **yes**                      |
| original fiction | [Reddit](https://www.reddit.com/)                                   | ✓ **yes**              | ✗ no                           |
| original fiction | [Quotev](https://www.quotev.com/)                                   | ✗ no                   | ✗ no                           |
| erotica          | [AdultFanFiction](http://www.adult-fanfiction.org/html-index.php)   | ✗ no                   | ✗ no                           |
| erotica          | [Literotica](https://www.literotica.com/)                           | ✗ no                   | ✓ **yes**                      |
| erotica          | [Hentai Foundry](https://www.hentai-foundry.com/)                   | ✗ no                   | ✓ **yes**                      |
| erotica          | [NajlepszaErotyka.com.pl](https://najlepszaerotyka.com.pl/)         | ✗ no                   | ✗ no                           |
| erotica          | [Nifty.org](https://www.nifty.org/nifty/)                           | ✗ no                   | ✗ no                           |

<sup>**[1]** **fiction-dl** is also capable of downloading whole collections and series.</sup>

It is also capable of reading stories saved in text files. You can put the HTML-formatted story in a raw text file and use **fiction-dl** to translate it to some more civilized format.

### Formatting stories

Downloaded stories are auto-formatted and saved in a few file formats:

| File Format                                                          | Requirements                                                          |
|----------------------------------------------------------------------|-----------------------------------------------------------------------|
| [HTML](https://en.wikipedia.org/wiki/HTML) (.html)                   | *None.*                                                               |
| [EPUB](https://en.wikipedia.org/wiki/EPUB) (.epub)                   | *None.*                                                               |
| [MOBI](https://en.wikipedia.org/wiki/Mobipocket) (.mobi)             | [Calibre](https://calibre-ebook.com/) installed on the machine.       |
| [OpenDocument](https://en.wikipedia.org/wiki/OpenDocument) (.odt)    | *None.*                                                               |
| [Portable Document Format](https://en.wikipedia.org/wiki/PDF) (.pdf) | [LibreOffice](https://www.libreoffice.org/) installed on the machine. |

### Embedding images

The application can download images found in story content and embed them in output files.

### Typographic corrections

**fiction-dl** automatically applies basic typographic corrections to the content of downloaded stories.

| Source Text                  | Corrected Text           |
|------------------------------|--------------------------|
| Lorem ipsum... dolor.        | Lorem ipsum… dolor.      |
| Lorem ipsum...dolor.         | Lorem ipsum… dolor.      |
| Lorem ipsum...... dolor.     | Lorem ipsum… dolor.      |
| Lorem ipsum , dolor.         | Lorem ipsum, dolor.      |
| Lorem ipsum????? Dolor.      | Lorem ipsum? Dolor.      |
| Lorem ipsum - dolor.         | Lorem ipsum — dolor.     |

### Packing stories

If you're downloading a lot of short stories, you can *pack* them into a single file, using the "-pack" command line option. This way you're adding only a single item to your Kindle book list, instead of many.

## ✿ Installation

You can install **fiction-dl** using *pip*:

    python3 -m pip install --upgrade fiction-dl

(If the package's already installed, this command will also update it.)

If you're running a Debian-derived Linux distribution, you might also need to install the following packages:

    apt-get install libgl1-mesa-glx libglib2.0-0 libmupdf-dev

(**fiction-dl** uses OpenCV for processing downloaded images, which requires them to be installed. PyMuPDF requires libmupdf-dev when it's being built from the source.)

## ✿ Usage

To download a story from a URL, simply type:

    fiction-dl URL

In order to download multiple stories, create a text file and place the URLs in it, each one in a separate line. Then type:

    fiction-dl YourFilesName

### Options

| Option            | Result                                                               |
|-------------------|----------------------------------------------------------------------|
| -h (--help)       | shows the overview of command-line options                           |
| -a                | authenticates the user to supported sites using interactive mode     |
| -c                | clears the cache before launching the application                    |
| -pack             | packs all downloaded stories inside one file (of each type)          |
| -v                | enables the (more) verbose mode                                      |
| -f                | overwrites output files (in case they already exist)                 |
| -d                | enables debug mode (saves some data useful for debugging)            |
| -no-images        | disables downloading images found in story content                   |
| -persistent-cache | preserves the cache after the application quits                      |
| -lo               | used to specify the path to the LibreOffice executable (soffice.exe) |
| -o                | used to specify the output directory path                            |


### Text File Extractor

Create a text file meant to contain the story. In its first lines type:

    LOCAL TEXT STORY
    *URL*
    *The Title of the Story*
    *The Author*
    *The One-Line Summary*

Follow it by the story's content, wrapped in HTML tags. Then call:

    fiction-dl FilePath.txt

You can insert chapter-breaks in the story by typing "CHAPTER BREAK LINE" in an empty line.

## ✿ License

**GNU GPL 3**. The text of the license is provided in the *LICENSE* file.

## ✿ Technical

### Changelogs

All the changelogs can be found in the *Docs/Changelogs.md* file.

### Documentation

You can generate code documentation using [**Doxygen**](https://www.doxygen.nl/index.html); the relevant configuration file is *Docs/Docs.doxygen*. Generated files will appear in the *Docs/Code Documentation* directory.

### Tests

Launching the **Integration Test** can be done by entering the *Tests* directory and executing the following code:

    python3 "Integration Test.py"
