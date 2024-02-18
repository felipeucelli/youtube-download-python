# YouTube download in python
A GUI that downloads videos from YouTube.

## Description
This application uses the pytube library to download from YouTube and the ffmpeg binary to manipulate the video and audio streams.

You can download single videos or entire playlists. In addition to being able to choose between downloading the video or just the audio.

Fully compatible with Windows and Linux systems (MacOS not tested).

## Features
* Support for downloading all available video and audio qualities
* Support for downloading the complete playlist
* Ability to download and merge subtitles into videos
* Ability to select a range from a playlist
* Keyword search support
* View and export a detailed list of downloaded files

## Quickstart
Installing dependencies and running the application

### Installing requirements
```bash
$ pip install -r requirements.txt
```

### Running the application
```bash
$ python main.py
```

## FAQ
### Error trying to download or search for a YouTube link
This program uses the [Pytube](https://github.com/pytube/pytube) library to search and download YouTube links. If you have related problems, you can search for the solution in an [issue](https://github.com/pytube/pytube/issues) in the library repository, or you can open an issue here.

## Prerequisites
* [Python3](https://www.python.org)
* [Pytubefix](https://github.com/JuanBindez/pytubefix)
* [Pillow](https://pillow.readthedocs.io/en/stable/)
* [Imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg)
* [ffmpeg_progress_yield](https://github.com/slhck/ffmpeg-progress-yield)
* [Tkinter](https://docs.python.org/3/library/tkinter.html)
