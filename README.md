# HDHR-DVR-Video-Process
Fast, autonomous, release style encodes from a TV tuner

HDHR DVR Process is a series of scripts used to process MPEG recordings made specifically using the HDHomeRun TV tuner and several 3rd party tools.

### What it does

What it does is strip the video file of the important information including the video and audio of course but also subtitles, chapter marks, and commercial stripping. It then encloses that information in a modern container (mkv or mp4) and transcodes the video file using the h.264 codec.

### Main Features

In addition to processing the video the script has these features:

- Renaming based on the filename of the recorded TV show. It will match the show name, find the season and episode, and rename the new file accordingly. 
- Uses HDHR DVR “Movies” folder to confirm the name of a movie with imdb and renames it in Movie Tittle (Movie Year) format.
- Adding subtitle and chapter information to recordings
- System to fix thetvdb mismatched show titles
- Archives the original file, a select number of used files, and a log of the process.
- Checking with the log file to see which programs are recordings before it runs so nothing is processed before recording is finished
- Made to run every half hour. Programs are ready to view in your library within an hour after it airs.
- Supplemental script to keep a certain number of most recent episodes and delete the archived original files
