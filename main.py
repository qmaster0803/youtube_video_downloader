import time
from   pytube import YouTube
from   pytube import Playlist
import pytube.exceptions
import os
import getpass
import urllib
import sys
import ffmpeg
import unicodedata
import re

import process_playlist
import process_video
import ui_utils

def replaceSpecialChars(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def mergeStreams(input_video, input_audio, output_video):
    video_stream = ffmpeg.input(input_video).video
    audio_stream = ffmpeg.input(input_audio).audio
    output = ffmpeg.output(video_stream, audio_stream, replaceSpecialChars(os.path.splitext(output_video)[0])+os.path.splitext(output_video)[1], vcodec="copy", acodec="copy")
    output.run(quiet=True)
    os.remove(input_video)
    os.remove(input_audio)

def main():
	#Welcome message and url request
    print("YouTube downloader v1.3")
    print("This program can download video or audio files from YouTube. Follow instructions below. You can exit from any step by pressing Ctrl+C.")
    print()
    url = input("Enter url to video or playlist: ")

    #Initializing settings
    wget_mode = True
    autocopy = False
    media_type = 0

    if(ui_utils.queryYN("Start download with wget? [Y/n]")):
        wget_mode = True
    else: wget_mode = False

    if(not wget_mode):
        if(ui_utils.queryYN("Autocopy links to clipboard? [Y/n]")):
            import pyperclip
            autocopy = True

    print()
    #check is this a plylist or a video
    parsed = urllib.parse.urlparse(url)
    playlist = False
    if(parsed.path == "/playlist"):
        print("Got playlist, processing...")
        playlist = True
    if(parsed.path == "/watch" or parsed.netloc == "youtu.be"):
        print("Got video, processing...")

    while(True):
        try:
            if(playlist): media_type = int(input("Please, select output format:\n1).MP4/.MP3\n2).WEBM/.OGG\nEnter number: "))
            else: media_type = int(input("Please, select output format:\n1).MP4/.MP3\n2).WEBM/.OGG\n3)PRO mode\nEnter number: "))
            if(media_type == 3 and not playlist):
                print("WARNING! In PRO mode all codecs will be shown, so output files can be corrupted if you made wrong choise.")
            if(media_type > 0 and media_type < 4 and not playlist): break
            if(media_type > 0 and media_type < 3 and playlist): break
        except ValueError: pass
    print()

    if(playlist):
        process_playlist.process(url, media_type, wget_mode, autocopy)
    else:
        process_video.process(url, media_type, wget_mode, autocopy)
    print("Done\n")

if(__name__ == "__main__"):
    try:
       main()
    except ConnectionResetError:
        print("Network error!")