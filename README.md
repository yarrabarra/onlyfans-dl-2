# OnlyFans Profile Downloader / Archiver v3
This tool downloads all photos/videos from an OnlyFans profile, creating a local archive.
You must be subscribed to the profile to download their content.

onlyfans-dl will create a directory named after the profile in the current working directory.
A subdirectory structure will be built depending on the options set.
Any existing media will be skipped, not redownloaded.
Content will be named as DATE_ID.EXT (e.g. 2021-04-17_123456.jpg)

#### Requires
Requires [Poetry](https://python-poetry.org/docs/#installation) and Python 3.10+
```shell
poetry install
```

#### Tagging Support


## Features
* Choose what type of content to download (photos, videos, posts, messages, purchases)
* Choose to create subfolders for each of the above, or combine them all into one folder
* Choose to sort posts with more than one photo into "albums" (subfolders)
* Download everything, or only the last &lt;integer&gt; days of content (posts only)

## TODO:
* Specify multiple profiles at once or use "all" keyword to get subscriptions dynamically
* Support for stories, archived
* Basic tagging via the Windows metadata service - `poetry install --extras=tagging` (Currently Windows only)
* Redesign checksum/filesize checking (incompatible with tagging currently)

## Usage
First make sure to set your session variables in the script and configure your options.

```
Usage: poetry run python src/main.py [OPTIONS]

Options:
  --targets TEXT            Which items to query
  --loglevel TEXT           Log level for logging
  --max-post-days INTEGER   Maximum number of days to go back for posts
  --albums BOOLEAN          Separate photos into subdirectories by post/album
                            (Single photo posts are not put into
                            subdirectories)
  --use-subfolders BOOLEAN  Use content type subfolders
                            (messages/archived/stories/purchased),or download
                            everything to /profile/photos and /profile/videos
  --help                    Show this message and exit.
  ```

## Session Variables
Requests to the API now need to be signed. This is an obfuscation technique from the developers to discourage scraping. Thanks for the most recent patch goes to [DIGITALCRIMINAL](https://github.com/DIGITALCRIMINAL/OnlyFans).

You need your browser's __user-agent__, onlyfans **sess**ion cookie, __x-bc__ HTTP header, and **user-id**. Here's how to get them

- Get your browser's user-agent here [ipchicken](https://ipchicken.com/) __You must update this every time your browser updates__
- Session Cookie
  - Login to OnlyFans as normal
  - Open the dev console Storage Inspector (`SHIFT+F9` on FireFox). or the __Application__ tab of Chrome DevTools
  - Click Cookies -> https://onlyfans.com
  - Copy the value of the `sess` cookie
- Headers: x-bc and user-id
  - Login to OnlyFans, goto home page
  - Open dev console `F12` -> Network tab (`Ctrl+Shift+E` in FireFox)
  - Click __Headers__ sub-tab (default)
  - Click on one of the JSON elements (may need to refresh page) and look under __request headers__ on the right

There are variables for each of these values at the top of the script. Make sure to update them every time you login or your browser updates.

## Contributing
PRs are welcome; be sure to take some time to familiarize yourself with OnlyFans' API if you would like to extend/modify the functionality of this script.
