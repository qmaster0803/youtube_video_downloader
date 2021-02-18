import time
from pytube import YouTube
from pytube import Playlist
import pytube.exceptions
import os
import getpass
import urllib
import sys
import ffmpeg

def queryYN(question):
    while(True):
        inp = input(question+" ")
        try:
            if(inp.split()[0] == "Y" or inp.split()[0] == "y"):
                return True
            if(inp.split()[0] == "N" or inp.split()[0] == "n"):
                return False
        except IndexError:
            return True

def showStreamSelector(video, calcMaxRes=False, media_type=3):
    video_stream = None
    audio_stream = None
    result_codec_type = None
    video_codec_type = 0 #for internal calculations
    audio_codec_type = 0 #for internal calculations
    #CODEC TYPES
    #-1 = only audio in mp4a codec
    #-2 = only audio in opus codec
    #1 = video&audio in mp4 container
    #2 = video&audio in webm container
    print("Choose stream:")
    while(True): #this loop is for returning user on choose again, if audio and video codecs in PRO mode can't be stored in one file without re-encoding
        streams = []
        i = 0
        max_res = 0
        for stream in video.streams:
            if(stream.type == "video" and stream.is_progressive == False):
                video_codec = stream.parse_codecs()[0].split(".")[0]
                show_stream = False
                if(media_type == 1 and video_codec == "av01"): show_stream = True
                if(media_type == 2 and video_codec == "vp9"): show_stream = True
                if(media_type == 3): show_stream = True
                if(show_stream):
                    i += 1
                    #print number
                    if(len(str(i)) == 2): print(str(i)+") Video;", end=" ")
                    else: print(str(i)+")  Video;", end=" ")
                    #print resolution
                    if(len(stream.resolution) == 5): print("Resolution: "+stream.resolution, end=" ")
                    else: print("Resolution: "+stream.resolution+" ", end=" ")
                    #print FPS
                    print("Framerate: "+str(stream.fps), end=" ")
                    #print codec
                    if(video_codec == "avc1"): print("Codec: AVC1 (.mp4)")
                    if(video_codec == "av01"): print("Codec: AV1  (.mp4)")
                    if(video_codec == "vp9"):  print("Codec: VP9  (.webm)")
                    streams.append(stream)
                    if(int(stream.resolution[:-1]) > max_res): max_res = int(stream.resolution[:-1])
            if(stream.type == "audio" and stream.is_progressive == False):
                audio_codec = stream.parse_codecs()[1].split(".")[0]
                show_stream = False
                if(media_type == 1 and audio_codec == "mp4a"): show_stream = True
                if(media_type == 2 and audio_codec == "opus"): show_stream = True
                if(media_type == 3): show_stream = True
                if(show_stream):
                    i += 1
                    streams.append(stream)
                    print(str(i)+") Audio;", "Bitrate: "+stream.abr, "Codec: "+stream.parse_codecs()[1].split(".")[0])
        #Requesting user's choise
        if(media_type == 1): #in MP4/MP3 mode
            video_stream_num = doUserInputNumber(len(streams)-1, "Choose stream: ")
            if(streams[video_stream_num].type == "video"):
                video_stream = streams[video_stream_num]
                audio_stream = selectAudioForVideo(video, video_stream)
            else:
                audio_stream = streams[video_stream_num]
        if(media_type == 2): #in WEBM/OGG mode
            video_stream_num = doUserInputNumber(len(streams)-1, "Choose stream: ")
            if(streams[video_stream_num].type == "video"):
                video_stream = streams[video_stream_num]
                audio_stream = selectAudioForVideo(video, video_stream)
            else:
                audio_stream = streams[video_stream_num]
        if(media_type == 3): #PRO mode
            video_stream_num = doUserInputNumber(len(streams)-1, "Enter VIDEO stream number (Enter zero to donwload only audio): ", allow_zero=True)
            if(video_stream_num != -1):
                video_stream = streams[video_stream_num]
            audio_stream_num = doUserInputNumber(len(streams)-1, "Enter AUDIO stream number: ")
            audio_stream = streams[audio_stream_num]

        if(video_stream != None): #detecting video codec (none for audio only mode)
            if(video_stream.parse_codecs()[0].split(".")[0] == "avc1" or video_stream.parse_codecs()[0].split(".")[0] == "av01"): video_codec_type = 1
            if(video_stream.parse_codecs()[0].split(".")[0] == "vp9"): video_codec_type = 2
        else:
            video_stream = 0

        #detecting audio codec
        if(audio_stream.parse_codecs()[1].split(".")[0] == "mp4a"): audio_codec_type = 1
        if(audio_stream.parse_codecs()[1].split(".")[0] == "opus"): audio_codec_type = 2

        #if codec types can be stored in one file, or only audio selected
        if(video_codec_type == audio_codec_type or video_codec_type == 0):
            break
        else:
            print("\n"*4)
            print("Chosen codecs can't be stored in one file without re-encoding. This program can't be used as re-encoder. Please, select other streams.")

    print("video_codec", video_codec_type)
    print("audio_codec", audio_codec_type)
    if(video_codec_type == 0 and audio_codec_type == 1): result_codec_type = -1
    if(video_codec_type == 0 and audio_codec_type == 2): result_codec_type = -2
    if(video_codec_type == 1): result_codec_type = 1
    if(video_codec_type == 2): result_codec_type = 2
    if(calcMaxRes): return video_stream, audio_stream, result_codec_type, max_res
    else: return video_stream, audio_stream, result_codec_type

def selectAudioForVideo(vid, video_stream):
    video_codec = video_stream.parse_codecs()[0].split(".")[0]
    audio_stream = None
    if(video_codec == "avc1" or video_codec == "av01"): preferred_audio_codec = "mp4a"
    if(video_codec == "vp9"): preferred_audio_codec = "opus"
    print("Preff audio:", preferred_audio_codec)
    for stream in vid.streams:
        if(stream.type == "audio" and stream.parse_codecs()[1].split(".")[0] == preferred_audio_codec):
            audio_stream = stream
    return audio_stream

def downloadFile(url, name, IDM_mode, autocopy):
    if(IDM_mode):
        downloader.download(url, os.getcwd(), output=name, lflag=5)
        idm_folder_name = urllib.parse.urlparse(url).netloc.split(".")[0]
        found = True
        while(found):
            found = False
            dirlist = os.listdir(os.path.join(os.getenv('APPDATA'), "IDM\\DwnlData\\", getpass.getuser()))
            for i in dirlist:
                if(i[:len(idm_folder_name)] == idm_folder_name):
                    found = True
    else:
        if(autocopy):
            print("Link generated and copied to clipboard. Please save it with", os.path.splitext(name)[1], "extension.")
            pyperclip.copy(url)
        else:
            print("Link generated. Please save it with", os.path.splitext(name)[1], "extension.")
            print("-"*20)
            print(url)
            print("-"*20)

def mergeStreams(input_video, input_audio, output_video):
    video_stream = ffmpeg.input(input_video).video
    audio_stream = ffmpeg.input(input_audio).audio
    output = ffmpeg.output(video_stream, audio_stream, output_video, vcodec="copy", acodec="copy")
    output.run(quiet=True)
    os.remove(input_video)
    os.remove(input_audio)

def doUserInputNumber(max_val, text="Enter number: ", allow_zero=False):
    while(True):
        try:
            res = int(input(text))-1
            if(allow_zero):
                if(res >= -1 and res <= max_val):
                    break
            else:
                if(res >= 0 and res <= max_val):
                    break
        except ValueError:
            pass
    return res

#Welcome message and url request
print("YouTube downloader v1.3")
print("This program can download video or audio files from YouTube. Follow instructions below. You can exit from any step by pressing Ctrl+C.")
print()
url = input("Enter url to video or playlist: ")

#Initializing settings
IDM_mode = True
autocopy = False
media_type = 0

if(queryYN("Start download with IDM? [Y/n]")):
    from downloader import IDMan
    downloader = IDMan()
else: IDM_mode = False

if(not IDM_mode):
    if(queryYN("Autocopy links to clipboard? [Y/n]")):
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
        media_type = int(input("Please, select output format:\n1).MP4/.MP3\n2).WEBM/.OGG\n3)PRO mode\nEnter number: "))
        if(media_type == 3):
            print("WARNING! In PRO mode all codecs will be shown, so output files can be corrupted if you made wrong choise.")
        if(media_type > 0 and media_type < 4): break
    except ValueError: pass
print()

if(playlist):
    playlist = Playlist(url)
    if(len(playlist) == 1):
        print("Got 1 video")
    else:
        print("Got", len(playlist), "videos")
    stream, audio_stream, codec_type = showStreamSelector(playlist, media_type=media_type)
else:
    vid = YouTube(url)
    print(vid.title)

    stream, audio_stream, codec_type = showStreamSelector(vid, media_type=media_type)
    
    print("codec:", codec_type)
    progressive_output = False
    if(codec_type == -1): #only audio in mp4a codec
        print("Downloading audio... ", end='', flush=True)
        url = audio_stream.url
        downloadFile(url, vid.title+".mp3", IDM_mode, autocopy)
        if(IDM_mode): print("done.")
    if(codec_type == -2): #only audio in opus codec
        print("Downloading audio... ", end='', flush=True)
        url = audio_stream.url
        downloadFile(url, vid.title+".ogg", IDM_mode, autocopy)
        if(IDM_mode): print("done.")

    if(codec_type == 1):
        progressive_output = True
        video_extension = ".mp4"
        audio_extension = ".mp3"
    if(codec_type == 2):
        progressive_output = True
        video_extension = ".webm"
        audio_extension = ".ogg"
    if(progressive_output):
        video_url = stream.url
        audio_url = audio_stream.url
        if(IDM_mode):
            print("Downloading video... ", end='', flush=True)
            downloadFile(video_url, "temp"+video_extension, IDM_mode, autocopy)
            print("done.", flush=True)
            print("Downloading audio... ", end='', flush=True)
            downloadFile(audio_url, "temp"+audio_extension, IDM_mode, autocopy)
            print("done.")
            print("Merging streams... ", end='', flush=True)
            mergeStreams("temp"+video_extension, "temp"+audio_extension, vid.title+video_extension)
            print("done.")
        else:
            downloadFile(video_url, "temp"+video_extension, IDM_mode, autocopy)
            input("Press enter to generate next link.")
            downloadFile(audio_url, "temp"+audio_extension, IDM_mode, autocopy)            
    print("Done\n")