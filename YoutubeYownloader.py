from pytubefix import Playlist
from pytubefix import YouTube
import subprocess
import os
import re

url = input("URL:")

def fix_audio(path):
    subprocess.run([
        "ffmpeg",
        "-i", path + ".webm",
        "-vn",
        "-c:a", "libmp3lame",  # proper MP3 encoder
        "-b:a", "192k",
        "-y",
              path + ".mp3"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def fix_title(title):
    nonowords=["Kasane Teto", "feat."]

    for word in nonowords:
        title = re.sub(re.escape(word),"",title)

    #title = re.sub(r'feat\.', "", title)
    title = re.sub(r'[\./]',"",title)
    title = re.sub(r'\(.*\)', "", title)
    title = re.sub(r'\s*$', "", title)
    title = re.sub(r'^\s*', "", title)



    return title

def process_video(path,video):
    title= "Title Grab Failed"
    try:
        audio = video.streams.get_audio_only()

        title=fix_title(video.title)
        print(title)
        audio.download(output_path=path, filename=f"{title}.webm")
        fix_audio(path + "\\" + f"{title}")
        os.remove(path + "\\" + f"{title}.webm")
    except:
        print("Failed: "+title)
        print("Continuing")


if "playlist" in url:
    playlist = Playlist(url)

    videos=playlist.videos

    print("Playlist: "+playlist.title)
    print("Playlist Size: "+str(len(videos)))

    for v in videos:

        process_video(playlist.title,v)


else:
    video = YouTube(url)

    process_video("output", video)




