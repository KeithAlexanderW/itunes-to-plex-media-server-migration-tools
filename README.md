# iTunes to Plex Media Server Migration Tools

## Summary
This is a Python package made up of Python scripts that I wrote to help me migrate my iTunes collection to Plex Media Server. 

## License
Completely open source and free. No warranties, expressed or implied.  

## Credits
Based loosely on the **[plex-imdb-ratings](https://github.com/haec0007/plex-imdb-ratings)** project on GitHub. 

### iTunes Plugin
It seems like Plex Media Server still supports the iTunes plugin (although I read that plugins in general were discontinued years ago). However, after a lot of research, I didn't try it. 
* It seems to be for new Plex Libraries only. I already had a Plex Library that I didn't want to delete or recreate.
* There is very little documentation for it. Researching and experimenting are fine, but rather time consuming. Like many, my time and resources are limited. As a seasoned software engineer, I'd rather learn a new-to-me language ([Python](https://www.python.org), [Python Docs](https://docs.python.org/3/)), and a new-to-me API ([Python PlexAPI](https://github.com/pkkid/python-plexapi), [Python PlexAPI Docs](https://python-plexapi.readthedocs.io/en/latest/introduction.html)). They both seemed very functional and well documented to me. 
* In retrospect, my iTunes music collection had been severely neglected (by me!) over the years and needed a lot of cleanup and TLC. I found thousands of duplicate tracks. I also found hundreds of files on disk that I never managed to get cataloged in iTunes. I reconnected with my music collection. 
* I wanted to empower myself to become an expert in Plex clients and servers.   

 
## Installation and Setup
1. It is assumed that you've already installed Python in your development environment. 
2. Clone or download this project to a folder/directory on your development machine. 
3. Install the required packages with pip:
   1. Open a terminal window in your environment. 
   2. [If you're using Visual Studio Code, you can do this by dropping to a terminal within that IDE.](https://stackoverflow.com/a/57310410/1472771)
   3. `pip install -r requirements.txt`
   4. If you encounter an error with Visual C++, "[Microsoft Visual C++ 14.0 or greater is required](https://stackoverflow.com/a/64262038/1472771)", try installing various versions of MS Build Tools; don't forget to restart your IDE and your machine.
   5. Visual Studio Code might want you to create a virtual Python environment. At the time of this writing, Python 3.13.1 was not working for me; try targeting Python 3.12.8 downloaded from the Microsoft Store.

## Configuration File
This is a YAML file that contains user-specific parameters needed to run the import script. You will need to create one that contains the following information:
- **plex**
  - **ip**: The IP address and port of your Plex server. You can also use a hostname if your DNS resolver provides the correct IP address.
  - **token**: [Your Plex authentication token.](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)  
- **itunes**
  - **itunes_xml_file**: The name of the Plex library containing tracks you want to rate.
    - In Windows 11, this file is typically located here: `C:\Users\[YourUsername]\Music\iTunes\iTunes Music Library.xml`
  - **log_tracks_with_zero_matches**: Log iTunes tracks that didn't match to any tracks in Plex Media Server


## The Tools
### Import Track Ratings exactly by Artist, Album and Track Name
This is a Python script for parsing an iTunes XML file, searching a Plex Media Server Library for matching tracks and loading the ratings. It searches by exact Artist, Album and Track Name titles. 

I like to run it several times, making corrections to my music library and the files as I go. I also like to run it on both the default Plex metadata system and [embedded metadata](https://support.plex.tv/articles/200381093-identifying-music-media-using-embedded-metadata/). 
```
python import_track_ratings_by_exact_artist_album_track.py <config_file>
```

### Import Track Ratings by Filename
This is a Python script for parsing an iTunes XML file, searching a Plex Media Server Library for matching tracks and loading the ratings. It searches strictly by filename. 

I like to run it several times, making corrections to my music library and the files as I go. I also like to run it on both the default Plex metadata system and [embedded metadata](https://support.plex.tv/articles/200381093-identifying-music-media-using-embedded-metadata/). 
```
python import_track_ratings_by_filename.py <config_file>
```

### Find Potentially Duplicated Albums
This is a Python script that connects to a Plex Library, downloads all the tracks, hash maps them and lists duplicate tracks (basically, the directory name). It does not use your iTunes XML file. 

It's possible for different artists to have the same album name, so it can't easily differentiate those. 
```
python find_potentially_duplicated_albums.py <config_file>
```

### Find Potentially Duplicated Tracks
This is a Python script that connects to a Plex Library, downloads all the tracks, hash maps the locations (basically, the filename) and lists duplicates. It does not use your iTunes XML file. 

It will help find real duplicates, but it will also likely find files that have the same filename in different albums. As an example, classical albums often have "01 - Overture.mp3" which will come up as a duplicate, though clearly it's not in most cases.
```
python find_potentially_duplicated_tracks.py <config_file>
```

### Get Filtering Fields
This is a Python script that connects to a Plex Library and get the filtering fields. Filtering fields are the ones that Plex displays as filters in the Web UI and other UIs.
```
python get_filtering_fields.py <config_file>
```

### Troubleshooting
This module is not intended to feature complete, nor is it intended to solve every problem, not solve every problem completely. Do keep in mind this is a bunch of Python (free) scripts, not an app. If you are not familiar with software engineering, scripting and self-guided troubleshooting, you might find it difficult to use these tools. Just keep swimming, as the fish says.  

That being said, I'll try to help when and where I can, as long as you've done your due diligence first. 
