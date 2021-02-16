import time
from pytube import YouTube
from pytube import Playlist
import pytube.exceptions
import os
import getpass
import urllib
import sys
import moviepy.editor as mpe




IDM_mode = True
autocopy = False

while(True):
    inp = input("Start download with IDM? [Y/n] ")
    if(inp.split()[0] == "Y" or inp.split()[0] == "y" or inp == ""):
        from downloader import IDMan
        downloader = IDMan()
        break
    if(inp.split()[0] == "N" or inp.split()[0] == "n"):
        IDM_mode = False
        break

if(not IDM_mode):
    while(True):
        inp = input("Autocopy links to clipboard? [Y/n] ")
        if(inp.split()[0] == "Y" or inp.split()[0] == "y" or inp == ""):
            import pyperclip
            autocopy = True
            break
        if(inp.split()[0] == "N" or inp.split()[0] == "n"):
            break




print("YouTube video downloader v1.2")
url = input("Enter url to video or playlist: ")

parsed = urllib.parse.urlparse(url)
playlist = False




if(parsed.path == "/playlist"):
    print("Got playlist, processing...")
    playlist = True
if(parsed.path == "/watch" or parsed.netloc == "youtu.be"):
    print("Got video, processing...")




if(playlist):
    print()
    playlist = Playlist(url)
    print("Got", len(playlist), "videos")
    print("Parsing video params, it can take long time")
    all_videos = []
    try:
        for i, vid in enumerate(playlist.videos):
            print(str(i+1)+"/"+str(len(playlist)))
            all_videos.append(vid)
    except pytube.exceptions.VideoRegionBlocked:
        print("Sorry, blocked in your region. Try changing VPN server.")
        sys.exit(0)

    print("Choose stream:")
    streams = []
    i = 0
    max_res = 0
    for i in all_videos[0].streams:
        print(i)
    i = 0
    for stream in all_videos[0].streams:
        if(stream.mime_type == "video/mp4"):
            i += 1
            print(str(i)+") Video;", "Resolution: "+stream.resolution, "Framerate: "+str(stream.fps))
            streams.append(stream)
            if(int(stream.resolution[:-1]) > max_res): max_res = int(stream.resolution[:-1])
        if(stream.mime_type == "audio/mp4"):
            i += 1
            streams.append(stream)
            print(str(i)+") Audio;", "Bitrate: "+stream.abr)

    stream = 0
    while(True):
        try:
            stream = int(input("Enter number: "))
            if(stream >= 1 and stream <= len(streams)):
                break
        except ValueError:
            print("Not a number!")

    print("Stream type got; Checking all videos.")
    if(max_res == streams[stream-1].resolution[:-1]): print("YES")
    input("e")
    for vid in all_videos:
        max_res2 = 0
        if(max_res == streams[stream-1].resolution[:-1]):
            for stream2 in vid.streams:
                if(stream2.mime_type == "video/mp4"):
                    if(int(stream2.resolution[:-1]) > max_res2): max_res2 = int(stream2.resolution[:-1])

    extension = ".mp3"

    for vid in playlist.videos:
        print("Downloading", vid.title)
        url = vid.streams.filter(type="audio")[0].url
        if(IDM_mode):
            downloader.download(url, os.getcwd(), output=vid.title+extension, lflag=5)
            idm_folder_name = urllib.parse.urlparse(url).netloc.split(".")[0]
            found = True
            while(found):
                found = False
                dirlist = os.listdir(os.path.join(os.getenv('APPDATA'), "IDM\\DwnlData\\", getpass.getuser()))
                for i in dirlist:
                    if(i[:len(idm_folder_name)] == idm_folder_name):
                        found = True
            print("Done\n")
        else:
            print("Link generated. Please paste it to your browser or other downloader.")
            print(url)
            print("\n"*5)

else:
    extension = ".mp3"
    vid = YouTube(url)
    print("Downloading", vid.title)

    print("Choose stream:")
    streams = []
    i = 0
    for stream in vid.streams:
        if(stream.mime_type == "video/mp4"):
            i += 1
            print(str(i)+") Video;", "Resolution: "+stream.resolution, "Framerate: "+str(stream.fps))
            streams.append(stream)
        if(stream.mime_type == "audio/mp4"):
            i += 1
            streams.append(stream)
            print(str(i)+") Audio;", "Bitrate: "+stream.abr)

    stream = 0
    while(True):
        try:
            stream = int(input("Enter number: "))
            if(stream >= 1 and stream <= len(streams)):
                break
        except ValueError:
            print("Not a number!")
    
    url = streams[stream-1].url
    if(streams[stream-1].type == "video"): extension = ".mp4"
    if(streams[stream-1].type == "audio"): extension = ".mp3"
    downloader.download(url, os.getcwd(), output=vid.title+extension, lflag=5)
    idm_folder_name = urllib.parse.urlparse(url).netloc.split(".")[0]
    found = True
    while(found):
        found = False
        dirlist = os.listdir(os.path.join(os.getenv('APPDATA'), "IDM\\DwnlData\\", getpass.getuser()))
        for i in dirlist:
            if(i[:len(idm_folder_name)] == idm_folder_name):
                found = True
    print("Done\n")