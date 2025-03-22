import os

# Base paths
BASE_PATH = os.getcwd()
BILIBILI_VIDEO_FOLDER = os.path.join(BASE_PATH, "bilibili_video")
PROCESSED_MEDIA_DIR = os.path.join(BASE_PATH, "processed_media")

# Folder structure constants
MEDIA_FOLDER_NAME = "112"  # Folder containing audio.m4s and video.m4s
SUBTITLE_FOLDER_NAME = "vi"  # Folder containing subtitle files
ENTRY_JSON_FILENAME = "entry.json"

# File names
AUDIO_FILENAME = "audio.m4s"
VIDEO_FILENAME = "video.m4s"

# File formats
DEFAULT_ENCODING = "utf-8"
JSON_EXTENSION = ".json"
SRT_EXTENSION = ".srt"
ASS_EXTENSION = ".ass"
M4S_EXTENSION = ".m4s"
MP4_EXTENSION = ".mp4"


# Subtitle settings
SUBTITLE_LANGUAGE_KEY = "en"  # Looking for English subtitles