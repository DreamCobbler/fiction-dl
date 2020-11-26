# 1.7.0

**General:**

- Create a logo for the application.
- Added the "f-dl" alias for the application executable.

**Extractors:**

- Added an extractor for Quotev.
- Added an extractor for WuxiaWorld.
- Added an extractor for WhoFic.com.
- Added an extractor for SamAndJack.net.

- Added collection support to the FF.net extractor.
- Added channel support to the HPFF extractor.
- Added channel support to the AdultFanfiction extractor.

**Formatters:**

- Improved the HTML output template.

**Bugfixes:**

- Resolved Issue #2.
- Resolved Issue #7.

- Improved the way in which the LibreOffice executable is located.
- Improved exception handling during image downloading process.

# 1.6.X

## 1.6.3

**General:**

- Added a missing dependency in the *setup.py* file (*dreamy-utilities*).

## 1.6.2

**General:**

- Another quick bugfix, once more about imports.

## 1.6.1

**General:**

- A quick bugfix regarding a wrong import in *__main__.py*.

# 1.6.0

**General:**

- Added the functionality of packing multiple stories inside a single file. (The "-pack" command line option.)

**Extractors:**

- Added an extractor for HarryPotterFanFiction.com.
- Added an extractor for Nifty.org.

- The AO3 extractor now supports downloading whole Collections.
- The AO3 extractor now supports downloading whole Series.
- The AO3 extractor is noticeably more optimized, reading data from the single-page story view instead of manually retrieving each chapter.

**Processing:**

- Improved story/chapter title processing.

**Bugfixes:**

- Fixed the problem with chapter titles on FF.net being combined. (I.e. "Chapter 1Chapter 2Chapter 3".)
- Fixed the problem with HTML entities being improperly encoded in output files.

**Stuff:**

- Moved *a lot* of utilities to the [Dreamy Utilities](https://github.com/DreamCobbler/dreamy-utilities) package.

# 1.5.0

**Extractors**:

- Introduced the concept of a *channel*; added channel support to a few extractors.
- Added an extractor for Questionable Questing.
- Added an extractor for FicWad.
- Added an extractor for Hentai Foundry.
- Added an extractor for Najlepsza Erotyka.

**Formatters**:

- Added a MOBI formatter.

**Processing:**

- Japanese story titles are now transliterated when put in file names.

**Bugfixes**:

- Fixed a few bugs in the extracters.
- Fixed a few bugs in the formatters.

**Stuff**:

- Significantly improved the user interface.
- Input arguments are now randomly re-ordered for processing.

# 1.4.0

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

# 1.3.0

**Processing:**

- Improved chapter title processing.

**Bugfixes:**

- Fixed a bug in the ODT formatter.
- Fixed a bug in the FF.net extractor.

# 1.2.0

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

# 1.1.1

**Stuff:**

- Fixed a mistake in the readme.

# 1.1.0

**General**:

- Reworked the way authentication works in all extractors.

**Extractors**:

- Added support for Reddit authentication.
- Expanded exception handling in the Reddit extractor.
- The Reddit extractor now handles extracting posts made by deleted users and suspended users.

**Processing**:

- Added some more processing for story titles.
