import os
import json
import re
import math
import shutil
import requests
from config import DEFAULT_ENCODING


def load_json(file_path, encoding=DEFAULT_ENCODING):
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file_path}")
        return {}


def write_json(file_path, data, encoding=DEFAULT_ENCODING):
    """Write JSON data to a file."""
    with open(file_path, 'w', encoding=encoding) as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def write_file(file_path, content, encoding=DEFAULT_ENCODING):
    """Write content to a file."""
    with open(file_path, 'w', encoding=encoding) as file:
        file.write(content)


def ensure_dir_exists(directory):
    """Ensure that a directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def format_srt_time(seconds):
    """Format a time in seconds to SRT format (HH:MM:SS,MS)."""
    hour = math.floor(seconds) // 3600
    minute = (math.floor(seconds) - hour * 3600) // 60
    sec = math.floor(seconds) - hour * 3600 - minute * 60
    min_sec = int(math.modf(seconds)[0] * 100)

    return f"{str(hour).zfill(2)}:{str(minute).zfill(2)}:{str(sec).zfill(2)},{str(min_sec).zfill(2)}"


def download_file(url, save_path):
    """Download a file from a URL and save it to the specified path."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            return save_path
        return None
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return None


def create_safe_filename(title):
    """
    Create a safe filename from a title.

    Args:
        title: The title to convert to a safe filename

    Returns:
        Safe filename string
    """
    if not title:
        return "Unknown"
    safe_title = "".join(c for c in title if c.isalnum()
                         or c in (' ', '_', '-')).strip()
    #safe_title = safe_title.replace(' ', '_')
    return safe_title


def extract_info_from_entry_json(entry_json_path):
    """
    Extract useful information from an entry.json file.

    Args:
        entry_json_path: Path to the entry.json file

    Returns:
        Dictionary containing extracted information
    """
    info = {
        # Default to folder name
        'title': os.path.basename(os.path.dirname(entry_json_path)),
        'episode_tag': '',
        'episode_id': '',
        'subtitle_url': '',
        'prefered_video_quality': ''
    }

    if not os.path.exists(entry_json_path):
        return info

    try:
        data = load_json(entry_json_path)

        # Extract title
        if 'title' in data:
            info['title'] = data['title']

        # Extract episode information
        if 'ep' in data:
            ep_data = data['ep']
            if 'page' in ep_data:
                info['episode_tag'] = ep_data['page']
            if 'episode_id' in ep_data:
                info['episode_id'] = ep_data['episode_id']

        # Extract subtitle URL
        if 'danmakuSubtitleReply' in data and 'subtitles' in data['danmakuSubtitleReply']:
            subtitle_list = data['danmakuSubtitleReply']['subtitles']
            for subtitle in subtitle_list:
                if subtitle.get('key') == 'en':
                    info['subtitle_url'] = subtitle.get('url', '')
                    break
        # Extract preferred video quality
        if 'prefered_video_quality' in data:
            info['prefered_video_quality'] = str(data['prefered_video_quality'])

    except Exception as e:
        print(f"Error reading entry.json: {str(e)}")

    return info


def format_tv_style_filename(title, season_number, episode_number):
    """
    Format a filename in TV show style: Title_S01E02

    Args:
        title: Show title
        season_number: Season number
        episode_number: Episode number

    Returns:
        Formatted filename string
    """
    safe_title = create_safe_filename(title)
    # Format season and episode numbers with leading zeros
    formatted_season = f"S{int(season_number):02d}"

    # Try to extract a numeric episode number
    try:
        if isinstance(episode_number, int):
            formatted_episode = f"E{episode_number:02d}"
        else:
            # Try to extract a number from the episode tag
            match = re.search(r'\d+', str(episode_number))
            if match:
                ep_num = int(match.group())
                formatted_episode = f"E{ep_num:02d}"
            else:
                # If no number found, use the tag as is
                formatted_episode = f"E{episode_number}"
    except (ValueError, TypeError):
        formatted_episode = f"E{episode_number}"

    return f"{safe_title} - {formatted_season}{formatted_episode}"


def copy_file_with_new_name(source_path, dest_dir, new_filename):
    """
    Copy a file to a destination with a new filename.

    Args:
        source_path: Path to the source file
        dest_dir: Destination directory
        new_filename: New filename (without directory path)

    Returns:
        Path to the new file or None if copy failed
    """
    ensure_dir_exists(dest_dir)
    dest_path = os.path.join(dest_dir, new_filename)

    try:
        shutil.copy2(source_path, dest_path)
        return dest_path
    except Exception as e:
        print(f"Error copying {source_path} to {dest_path}: {str(e)}")
        return None


def create_metadata_file(output_path, title, season_number, episode_tag, 
                        audio_path, video_path, source_folder, mkv_path=None, 
                        subtitle_paths=None):
    """
    Create a metadata text file with episode information.
    
    Args:
        output_path: Path to write the metadata file
        title: Episode title
        season_number: Season number
        episode_tag: Episode tag/number
        audio_path: Path to the audio file
        video_path: Path to the video file
        source_folder: Original source folder
        mkv_path: Path to the MKV file (optional)
        subtitle_paths: Dictionary of subtitle paths by language code (optional)
        
    Returns:
        Path to the metadata file or None if creation failed
    """
    try:
        with open(output_path, 'w', encoding=DEFAULT_ENCODING) as f:
            f.write(f"Title: {title}\n")
            f.write(f"Season: {season_number}\n")
            f.write(f"Episode: {episode_tag}\n")
            f.write(f"Audio file: {audio_path}\n")
            f.write(f"Video file: {video_path}\n")
            
            if mkv_path:
                f.write(f"MKV file: {mkv_path}\n")
                
            if subtitle_paths and isinstance(subtitle_paths, dict):
                f.write("Subtitles:\n")
                for lang, path in subtitle_paths.items():
                    f.write(f"  {lang}: {path}\n")
                    
            f.write(f"Original folder: {source_folder}\n")
        return output_path
    except Exception as e:
        print(f"Error creating metadata file {output_path}: {str(e)}")
        return None
