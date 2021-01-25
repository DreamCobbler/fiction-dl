# ![Logo](/Stuff/Logo%20(64).png?raw=true) [fiction-dl](https://github.com/DreamCobbler/fiction-dl) (*1.8.1*)

![Screenshot (Windows 10)](/Stuff/Screenshot%20(Windows%2010).png?raw=true)
![Screenshot (Linux Mint 20)](/Stuff/Screenshot%20(Linux%20Mint%2020).png?raw=true)

**fiction-dl** is a command-line utility designed to download works of (fan)fiction from the web and save them in a few portable file formats. It requires a [Python](https://www.python.org/) interpreter installed, version 3.8 or higher.

The application currently supports almost two dozen websites and six output file formats; the latter being: HTML, ODT, PDF, EPUB and MOBI. It's able to download images found in story content, as well as capable of applying basic typographic corrections to the content itself.

## ✿ Table of Contents

1. [Features](#features).
2. [Installation](#installation).
3. [Usage](#usage).
4. [License](#license).
5. [Technical](#technical).

## ✿ Features

### Downloading stories

**fiction-dl** can download stories from a multitude of sites - in some cases, it also supports downloading all stories published by any specific user (which is called downloading stories from a *channel*).

In a select few sites, it allows you to log-in to the site using the command-line; this functionality allows the user to access subforums closed to guest viewers, like the *Fandom* category on [AlternateHistory.com](https://www.alternatehistory.com/forum/), or quarantined subreddits on [Reddit](https://www.reddit.com/).

| \#   | Category         | Site                                                                | Authentication support | Channel support                |
|------|------------------|---------------------------------------------------------------------|------------------------|--------------------------------|
| *1*  | fanfiction       | [Archive of Our Own](https://archiveofourown.org/)                  | ✓ **yes**              | ✓ **yes <sup>[1]</sup>**       |
| *2*  | fanfiction       | [FanFiction.net](https://www.fanfiction.net/)                       | ✗ no                   | ✓ **yes <sup>[2]</sup>**       |
| *3*  | fanfiction       | [FicWad.com](https://ficwad.com/)                                   | ✗ no                   | ✓ **yes**                      |
| *4*  | fanfiction       | [SpaceBattles.com](https://forums.spacebattles.com/)                | ✓ **yes**              | ✗ no                           |
| *5*  | fanfiction       | [SufficientVelocity.com](https://forums.sufficientvelocity.com/)    | ✓ **yes**              | ✗ no                           |
| *6*  | fanfiction       | [AlternateHistory.com](https://www.alternatehistory.com/forum/)     | ✓ **yes**              | ✗ no                           |
| *7*  | fanfiction       | [QuestionableQuesting.com](https://forum.questionablequesting.com/) | ✗ no                   | ✗ no                           |
| *8*  | fanfiction       | [HarryPotterFanFiction.com](https://harrypotterfanfiction.com/)     | ✗ no                   | ✓ **yes**                      |
| *9*  | fanfiction       | [WhoFic.com](https://www.whofic.com/)                               | ✗ no                   | ✓ **yes <sup>[3]</sup>**       |
| *10* | fanfiction       | [SamAndJack.net](http://www.samandjack.net/fanfics/index.php)       | ✗ no                   | ✓ **yes**                      |
| *11* | fanfiction       | [Ralst.com](http://ralst.com/)                                      | ✗ no                   | ✗ no                           |
| *12* | original fiction | [Fiction Press](https://www.fictionpress.com/)                      | ✗ no                   | ✓ **yes**                      |
| *13* | original fiction | [Reddit](https://www.reddit.com/)                                   | ✓ **yes**              | ✗ no                           |
| *14* | original fiction | [Quotev](https://www.quotev.com/)                                   | ✗ no                   | ✗ no                           |
| *15* | original fiction | [Wuxiaworld](https://www.wuxiaworld.com/)                           | ✗ no                   | ✗ no                           |
| *16* | erotica          | [AdultFanFiction](http://www.adult-fanfiction.org/html-index.php)   | ✗ no                   | ✓ **yes**                      |
| *17* | erotica          | [Literotica](https://www.literotica.com/)                           | ✗ no                   | ✓ **yes**                      |
| *18* | erotica          | [Hentai Foundry](https://www.hentai-foundry.com/)                   | ✗ no                   | ✓ **yes**                      |
| *19* | erotica          | [NajlepszaErotyka.com.pl](https://najlepszaerotyka.com.pl/)         | ✗ no                   | ✗ no                           |
| *20* | erotica          | [Nifty.org](https://www.nifty.org/nifty/)                           | ✗ no                   | ✗ no                           |
| *21* | erotica          | [asstr.org/~Kristen](https://www.asstr.org/~Kristen/)               | ✗ no                   | ✗ no                           |

- <sup>**[1]** **fiction-dl** is also capable of downloading whole collections and series.</sup>
- <sup>**[2]** The application supports also downloading entire collections.</sup>
- <sup>**[3]** The application supports downloading whole series as well.</sup>

It is also possible to process stories stored in local files. You can put the HTML-formatted story in a raw text file and use **fiction-dl** to reformat it in all of its output file formats.

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

**fiction-dl** automatically applies basic typographic corrections to the content of downloaded stories. For example:

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

    f-dl URL

In order to download multiple stories, create a text file and place the URLs in it, each one in a separate line. Then type:

    f-dl YourFilesName

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

    f-dl FilePath.txt

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
