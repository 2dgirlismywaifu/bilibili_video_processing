"""
Main processing module for Bilibili anime content.
Handles extraction, organization, and processing of video, audio, and subtitle files.
"""

import os
from utils import (
    ensure_dir_exists, copy_file_with_new_name, create_metadata_file,
    extract_info_from_entry_json, format_tv_style_filename
)
from config import *
import message
from jsonToSRT import convert_json_to_srt
from multiplexer import multiplex_to_mkv


def download_en_subtitle(entry_info, season_number, output_base_filename=None):
    """
    Download English subtitle from Bilibili and convert to SRT format.

    Args:
        entry_info: Dictionary with episode information
        season_number: Season number for TV style naming
        output_base_filename: Optional custom base filename (defaults to TV style format)

    Returns:
        Path to the subtitle file or None if download failed
    """
    subtitle_url = entry_info.get('subtitle_url', '')
    title = entry_info.get('title', 'Unknown')
    episode_tag = entry_info.get('episode_tag', '')

    if not subtitle_url:
        message.subtitle_missing(title, episode_tag)
        return None

    # Create output directory
    ensure_dir_exists(PROCESSED_MEDIA_DIR)

    # Format file name
    if not output_base_filename:
        output_base_filename = format_tv_style_filename(
            title, season_number, episode_tag)

    # Determine extension from URL
    extension = JSON_EXTENSION if '.json' in subtitle_url.lower() else ASS_EXTENSION
    lang_extension = f".en{extension}"

    # Download subtitle file
    subtitle_file_path = os.path.join(
        PROCESSED_MEDIA_DIR, f"{output_base_filename}{lang_extension}")

    if not os.path.exists(subtitle_file_path):
        from utils import download_file
        if not download_file(subtitle_url, subtitle_file_path):
            message.subtitle_process_failed(title, episode_tag)
            return None

    message.subtitle_download_success(title, episode_tag)

    # Convert JSON to SRT if needed
    if extension == JSON_EXTENSION:
        srt_file_path = subtitle_file_path.replace(
            lang_extension, f".en{SRT_EXTENSION}")
        if convert_json_to_srt(subtitle_file_path, srt_file_path):
            message.subtitle_convert_success(srt_file_path)
            return srt_file_path

    return subtitle_file_path


def process_local_subtitle(season_folder, entry_info, season_number, output_base_filename=None):
    """
    Process local subtitle files found in the vi folder.

    Args:
        season_folder: Path to the season folder
        entry_info: Dictionary with episode information
        season_number: Season number for TV style naming
        output_base_filename: Optional custom base filename (defaults to TV style format)

    Returns:
        Dictionary of subtitle paths by language code
    """
    title = entry_info.get('title', os.path.basename(season_folder))
    episode_tag = entry_info.get('episode_tag', '')

    vi_folder = os.path.join(season_folder, SUBTITLE_FOLDER_NAME)
    if not os.path.exists(vi_folder):
        message.folder_not_found("subtitle", season_folder)
        return {}

    # Format base filename
    if not output_base_filename:
        output_base_filename = format_tv_style_filename(
            title, season_number, episode_tag)

    # Create output directory
    ensure_dir_exists(PROCESSED_MEDIA_DIR)

    subtitle_paths = {}

    # Process subtitle files
    for extension in (JSON_EXTENSION, ASS_EXTENSION):
        subtitle_files = [f for f in os.listdir(
            vi_folder) if f.endswith(extension)]
        for subtitle_file in subtitle_files:
            source_path = os.path.join(vi_folder, subtitle_file)
            dest_filename = f"{output_base_filename}.vi{extension}"
            output_path = os.path.join(PROCESSED_MEDIA_DIR, dest_filename)

            # Copy if it doesn't exist
            if not os.path.exists(output_path):
                copy_file_with_new_name(
                    source_path, PROCESSED_MEDIA_DIR, dest_filename)
                message.info(f"Copied {extension} subtitle: {output_path}")

            # Convert JSON to SRT
            if extension == JSON_EXTENSION:
                srt_path = output_path.replace(JSON_EXTENSION, SRT_EXTENSION)
                if convert_json_to_srt(output_path, srt_path):
                    message.subtitle_convert_success(srt_path)
                    subtitle_paths['vi'] = srt_path
            else:
                subtitle_paths['vi'] = output_path

    return subtitle_paths


def find_subtitle_files(base_filename):
    """
    Find existing subtitle files for a given base filename.

    Args:
        base_filename: Base filename to search for subtitle files

    Returns:
        Dictionary of subtitle paths by language code
    """
    subtitle_paths = {}

    # Check for English subtitle (downloaded)
    for lang, prefix in [('en', '.en'), ('vi', '.vi')]:
        for ext in (SRT_EXTENSION, ASS_EXTENSION):
            path = os.path.join(PROCESSED_MEDIA_DIR,
                                f"{base_filename}{prefix}{ext}")
            if os.path.exists(path):
                subtitle_paths[lang] = path
                break

    return subtitle_paths


def process_media_files(season_folder, season_number=1):
    """
    Process media files and create MKV with video, audio, and subtitles.

    Args:
        season_folder: Path to the season folder
        season_number: Season number for TV style naming

    Returns:
        Dictionary with paths to processed files or None if processing failed
    """
    # Get basic information
    entry_json_path = os.path.join(season_folder, ENTRY_JSON_FILENAME)
    entry_info = extract_info_from_entry_json(entry_json_path)

    title = entry_info.get('title', os.path.basename(season_folder))
    episode_tag = entry_info.get('episode_tag', '')
    prefered_video_quality = entry_info.get('prefered_video_quality')

    if not prefered_video_quality:
        message.error(
            f"Could not determine video quality folder for {season_folder}")
        return None

    # Find media folder
    media_folder = os.path.join(season_folder, prefered_video_quality)
    if not os.path.exists(media_folder):
        message.folder_not_found(
            f"video quality folder ({prefered_video_quality})", season_folder)
        return None

    # Create output folder
    ensure_dir_exists(PROCESSED_MEDIA_DIR)

    # Check for source files
    audio_path = os.path.join(media_folder, AUDIO_FILENAME)
    video_path = os.path.join(media_folder, VIDEO_FILENAME)
    if not (os.path.exists(audio_path) and os.path.exists(video_path)):
        message.media_files_missing(media_folder)
        return None

    # Format standard filename
    tv_style_filename = format_tv_style_filename(
        title, season_number, episode_tag)

    # Process files
    try:
        # Copy media files
        output_audio_filename = f"{tv_style_filename}_{AUDIO_FILENAME}"
        output_video_filename = f"{tv_style_filename}_{VIDEO_FILENAME}"

        output_audio_path = copy_file_with_new_name(
            audio_path, PROCESSED_MEDIA_DIR, output_audio_filename)
        output_video_path = copy_file_with_new_name(
            video_path, PROCESSED_MEDIA_DIR, output_video_filename)

        if output_audio_path and output_video_path:
            message.media_copied(title, PROCESSED_MEDIA_DIR)

        # Find or create subtitle files
        subtitle_paths = find_subtitle_files(tv_style_filename)

        # Create MKV
        output_mkv_path = os.path.join(
            PROCESSED_MEDIA_DIR, f"{tv_style_filename}.mkv")
        mkv_path = multiplex_to_mkv(
            output_video_path,
            output_audio_path,
            output_mkv_path,
            subtitle_paths,
            title
        )

        # Create metadata
        metadata_path = os.path.join(
            PROCESSED_MEDIA_DIR, f"{tv_style_filename}_metadata.txt")
        create_metadata_file(
            metadata_path,
            title,
            season_number,
            episode_tag,
            output_audio_path,
            output_video_path,
            season_folder,
            mkv_path,
            subtitle_paths
        )

        return {
            'audio': output_audio_path,
            'video': output_video_path,
            'mkv': mkv_path,
            'metadata': metadata_path,
            'subtitles': subtitle_paths,
            'quality': prefered_video_quality
        }

    except Exception as e:
        message.error(f"Error processing media files for {title}: {str(e)}")
        return None


def is_valid_season_folder(folder_path):
    """
    Check if a folder is a valid anime season folder.

    Args:
        folder_path: Path to check

    Returns:
        True if it's a valid season folder, False otherwise
    """
    # Check for entry.json
    has_entry_json = os.path.exists(
        os.path.join(folder_path, ENTRY_JSON_FILENAME))
    has_subtitle_folder = os.path.exists(
        os.path.join(folder_path, SUBTITLE_FOLDER_NAME))

    # Check for quality folders based on entry.json
    has_media_folder = False
    if has_entry_json:
        entry_info = extract_info_from_entry_json(
            os.path.join(folder_path, ENTRY_JSON_FILENAME))
        prefered_video_quality = entry_info.get('prefered_video_quality')

        if prefered_video_quality and os.path.exists(os.path.join(folder_path, prefered_video_quality)):
            has_media_folder = True

    # Check for any folder containing media files
    if not has_media_folder:
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                if (os.path.exists(os.path.join(item_path, AUDIO_FILENAME)) and
                        os.path.exists(os.path.join(item_path, VIDEO_FILENAME))):
                    has_media_folder = True
                    break

    return has_entry_json or has_media_folder or has_subtitle_folder


def process_season_folder(season_folder, season_number=1):
    """
    Process a single anime season folder.

    Args:
        season_folder: Path to the season folder
        season_number: Season number for TV style naming

    Returns:
        True if processing was successful, False otherwise
    """
    message.season_processing(os.path.basename(season_folder))

    # Get season info
    entry_json_path = os.path.join(season_folder, ENTRY_JSON_FILENAME)
    if not os.path.exists(entry_json_path):
        message.file_not_found(ENTRY_JSON_FILENAME, season_folder)
        return False

    entry_info = extract_info_from_entry_json(entry_json_path)

    # Format standard filename
    title = entry_info.get('title', os.path.basename(season_folder))
    episode_tag = entry_info.get('episode_tag', '')
    tv_style_filename = format_tv_style_filename(
        title, season_number, episode_tag)

    # Process all content
    download_en_subtitle(entry_info, season_number, tv_style_filename)
    process_local_subtitle(season_folder, entry_info,
                           season_number, tv_style_filename)
    process_media_files(season_folder, season_number)

    return True


def find_season_folders(parent_folder, max_depth=3, current_depth=0):
    """
    Recursively find all valid season folders.

    Args:
        parent_folder: Parent folder to start the search from
        max_depth: Maximum recursion depth
        current_depth: Current recursion depth

    Returns:
        List of valid season folder paths
    """
    if current_depth > max_depth:
        return []

    season_folders = []

    # Get all subfolders
    subfolders = [os.path.join(parent_folder, f) for f in os.listdir(parent_folder)
                  if os.path.isdir(os.path.join(parent_folder, f))]

    for folder in subfolders:
        if is_valid_season_folder(folder):
            season_folders.append(folder)
        else:
            # If not a valid season folder, search inside it
            season_folders.extend(find_season_folders(
                folder, max_depth, current_depth + 1))

    return season_folders


def process_all_seasons(bilibili_folder, season_number=1):
    """
    Process all anime seasons in the bilibili_video folder.

    Args:
        bilibili_folder: Path to the bilibili_video folder
        season_number: Season number for TV style naming

    Returns:
        None
    """
    if not os.path.exists(bilibili_folder):
        message.folder_not_found("Bilibili video", "")
        return

    # Find all season folders recursively
    season_folders = find_season_folders(bilibili_folder)

    if not season_folders:
        message.warning(
            f"No valid anime season folders found in {bilibili_folder}")
        return

    message.info(f"Found {len(season_folders)} anime season folders")

    # Process each season folder
    for season_folder in season_folders:
        process_season_folder(season_folder, season_number)


def get_season_number():
    """
    Get season number from user input.

    Returns:
        Integer representing the season number (1-99)
    """
    while True:
        try:
            season_input = input("Enter the season number (1-99): ")
            season_number = int(season_input)
            if 1 <= season_number <= 99:
                return season_number
            else:
                print("Please enter a number between 1 and 99.")
        except ValueError:
            print("Please enter a valid number.")


if __name__ == "__main__":
    # Get season number from user
    season_number = get_season_number()
    message.info(f"Processing anime as Season {season_number}")

    # Process all seasons with the specified season number
    process_all_seasons(BILIBILI_VIDEO_FOLDER, season_number)
