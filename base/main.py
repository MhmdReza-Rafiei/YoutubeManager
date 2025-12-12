import yt_dlp
import time
from os import makedirs as osmakedirs
from typing import Dict

_print = print
def print(*args, anim: bool = True, end="\n" , flush = False):
    if anim:
       time.sleep(0.3)
    _print(*args, end=end , flush = flush)

DOWNLOAD_PATH = "data"
osmakedirs(DOWNLOAD_PATH, exist_ok=True)


CONFIG_FILE = 'config'
CONFIG = {
    'User_Name': None,
    'Defult_Urls': []
}


QUALITY = {
    "highest": "bestvideo+bestaudio/best",
    "high": "best[height<=720]",
    "mid": "best[height<=480]",
    "low": "best[height<=360]",
    "lowest": "best[height<=144]",
    "audio": "bestaudio/best"
}

# ====================== Optional Functions ======================
def getQuality() -> QUALITY:
    return QUALITY
# ====================== Actions ======================
def Download(url: str, type: str = "video", format: str = "mp4", quality: str = "highest" , thumbnail:bool = False , organize: bool = True) -> yt_dlp.YoutubeDL:
    quality = QUALITY[quality]
    if not quality:
        print("[Error] Not Valid Quality")

    if type == "audio":
        quality = "bestaudio/best"
        postprocessors = [
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'},
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format.lower(),
                'preferredquality': '192',
            }, 
        ]

    elif type == "video":
        quality = QUALITY.get(quality, "best")
        postprocessors = [
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'},
        ]

    elif type == "test":
        print(f"[Testing] Url: {url}")
        quality = None
        postprocessors = []
        ydl_opts['skip_download'] = True

    else:
        print(f"[Error] Invalid type: '{type}'. Use 'video', 'audio', or 'test'",anim=True)
        return

    output = '%(title)s.%(ext)s'
    if organize:
        output = f'%(uploader)s/{type.title()}/%(title)s.%(ext)s'
        if 'playlist' in url.lower() or 'channel' in url.lower():
            output = f'%(uploader)s/{type.title()}/%(playlist)s/%(playlist_index|NA)s - %(title)s.%(ext)s'

    ydl_opts = {
        'format': quality,
        'outtmpl': f"{DOWNLOAD_PATH}/{output}",
        'merge_output_format': 'mkv' if type == "video" else None,
        'postprocessors': postprocessors,
        'writethumbnail': thumbnail,
        'ignoreerrors': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Unknown')
            print(f"[Download] {title} [Type: {type.title()} / Quality: {quality}]",anim=True)
            return True
    except Exception as e:
        print(f"[Error] While Downloading: {e}",anim=True)
        return False

def getInfo(url: str) -> Dict:
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extract_flat': 'in_playlist',
        'extractor_args': {
            'youtube': {
                'skip': ['authcheck'],
                'player_skip': ['js', 'configs', 'webpage'], 
                'max_comments': 0, 
            }
        },
        'ignoreerrors': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        if info is None:
            print("[Error] No info extracted (possibly private or removed)",anim=True)
            return None

        return info

    except Exception as e:
        print(f"[Error] Failed to extract info: {e}",anim=True)
        return None
