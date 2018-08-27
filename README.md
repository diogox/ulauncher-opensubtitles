# OpenSubtitles (ULauncher Extension)

This is an extension for [ULauncher](https://ulauncher.io/), a mac-like application launcher for linux. 

For this extension to work, install the following modules:
```
pip install --user beautifulsoup4
```

Available Commands: (TODO)
`srt ` - Shows you the menu
`srt movie %s` - Shows search results for %s in OpenSubtitles
`srt movie id %d` - Show subtitles available for the movie with the id %d (in the default language, chosen in the preferences)
`srt movie id %d en` - Same as above, but with 'en' (English) as the language of choice for the subtitles
`srt tv %s` - (Same as for 'movie')
`srt tv id %d` - (Same as for 'movie')
`srt movie id %d en` - (Same as for 'movie')

TODO in the future:
`srt file` - Detects a selected video file in the file explorer and searches for subtitles for it.

Credit:
    -> Most icon flags were downloaded from [flaticon](https://www.flaticon.com/packs/rectangular-country-simple-flags?style_id=118&family_id=41&group_id=1&category_id=85)