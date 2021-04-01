import download_utils

#just query [Y/N]; default (enter) = true
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

#for creating selectors
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

#a lot of stuff here; shows video's stream selector
#media_type:
#1 - .MP4/.MP3
#2 - .WEBM/.OGG
#3 - PRO mode, all streams shown, but there is a check for incompatible video/audio
def showStreamSelector(video, media_type=3):
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
    if(media_type == 1 or media_type == 3): print("AVC1 provides best quality, than AV1. But AV1 files is smaller.")
    while(True): #this loop is for returning user on choose again, if audio and video codecs in PRO mode can't be stored in one file without re-encoding
        streams = []
        i = 0
        for stream in video.streams:
            if(stream.type == "video" and stream.is_progressive == False):
                video_codec = stream.parse_codecs()[0].split(".")[0]
                show_stream = False
                if(media_type == 1 and (video_codec == "avc1" or video_codec == "av01")): show_stream = True
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
                audio_stream = download_utils.selectAudioForVideo(video, video_stream)
            else:
                audio_stream = streams[video_stream_num]
        if(media_type == 2): #in WEBM/OGG mode
            video_stream_num = doUserInputNumber(len(streams)-1, "Choose stream: ")
            if(streams[video_stream_num].type == "video"):
                video_stream = streams[video_stream_num]
                audio_stream = download_utils.selectAudioForVideo(video, video_stream)
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

    if(video_codec_type == 0 and audio_codec_type == 1): result_codec_type = -1
    if(video_codec_type == 0 and audio_codec_type == 2): result_codec_type = -2
    if(video_codec_type == 1): result_codec_type = 1
    if(video_codec_type == 2): result_codec_type = 2
    return video_stream, audio_stream, result_codec_type