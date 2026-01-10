from pytubefix import Playlist
from pytubefix import YouTube

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, APIC

from PIL import Image

import subprocess
import os
import re
import urllib


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

    title = re.sub(r'[\./]',"",title)
    #title = re.sub(r'\(.*\)', "", title)
    title = re.sub(r'\s*$', "", title)
    title = re.sub(r'^\s*', "", title)



    return title

def download_thumbnail(video):
    try:
        thumbnail_url = video.thumbnail_url
        # download image
        urllib.request.urlretrieve(thumbnail_url, "thumbnail.jpg")

    except Exception as e:
        print(f"An error occurred: {e}")

def crop_thumbnail():
    #open image
    img = Image.open("thumbnail.jpg")
    width, height = img.size

    side_length = min(width, height)

    #calculate for maximal square
    left = (width - side_length) // 2
    top = (height - side_length) // 2
    right = (width + side_length) // 2
    bottom = (height + side_length) // 2

    #crop
    square_img = img.crop((left, top, right, bottom))

    #save
    square_img.save("thumbnail.jpg", "JPEG")

def add_metadata(audio_file_path, video, playlist=None):
    #check exists
    if not os.path.exists(audio_file_path):
        print(f"Error: {audio_file_path} not found.")
    else:
        #load mp3
        try:
            audio = EasyID3(audio_file_path)
        except Exception:
            #add ID3 tag
            audio = mutagen.File(audio_file_path, easy=True)
            audio.add_tags()

        #set metadata
        audio['title'] = video.title
        audio['artist'] = re.sub(r' - Topic',"",video.author)
        if playlist:
            audio['album'] = playlist

        #save
        audio.save()

        #album art
        audio_full = ID3(audio_file_path)


        download_thumbnail(video)
        crop_thumbnail()

        with open("thumbnail.jpg", 'rb') as albumart:
            audio_full['APIC'] = APIC(
                encoding=3,  # UTF-8
                mime='image/jpeg',
                type=3,  # Cover front
                desc='Cover',
                data=albumart.read()
            )
        audio_full.save()

def process_video(path,video, playlist=None):
    title= "Title Grab Failed"

    try:
        audio = video.streams.get_audio_only()

        title=fix_title(video.title)
        print(title)
        audio.download(output_path=path, filename=f"{title}.webm")
        fix_audio(path + "\\" + f"{title}")
        os.remove(path + "\\" + f"{title}.webm")

        add_metadata(path + "\\" + f"{title}.mp3", video,playlist)
    except None:
        print("Failed: "+title)
        print("Continuing")



if "playlist" in url:
    playlist = Playlist(url)

    videos=playlist.videos

    print("Playlist: "+playlist.title)
    print("Playlist Size: "+str(len(videos)))

    for v in videos:

        process_video(playlist.title,v,playlist.title)

else:

    video = YouTube(url)
    process_video("output", video)




