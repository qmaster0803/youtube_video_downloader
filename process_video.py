from pytube import YouTube
import download_utils
import ui_utils

def process(url, media_type, wget_mode, autocopy):
    vid = YouTube(url)
    print(vid.title)

    stream, audio_stream, codec_type = ui_utils.showStreamSelector(vid, media_type=media_type)
    
    progressive_output = False
    if(codec_type == -1): #only audio in mp4a codec
        print("Downloading audio... ", end='', flush=True)
        url = audio_stream.url
        downloadFile(url, vid.title+".mp3", wget_mode, autocopy)
        if(wget_mode): print("done.")
    if(codec_type == -2): #only audio in opus codec
        print("Downloading audio... ", end='', flush=True)
        url = audio_stream.url
        downloadFile(url, vid.title+".ogg", wget_mode, autocopy)
        if(wget_mode): print("done.")

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
        download_utils.doOutput(video_url, video_extension, audio_url, audio_extension, wget_mode, autocopy)