import os
from jsonToSRT import convert_json_to_srt
from utils import (
    ensure_dir_exists, download_file, extract_info_from_entry_json, format_tv_style_filename,
    copy_file_with_new_name, create_metadata_file
)
from config import *
import message


def download_en_subtitle(entry_info, season_number):
    """
    Download English subtitle from Bilibili and convert to SRT format.

    Args:
        entry_info: Dictionary with episode information
        season_number: Season number for TV style naming

    Returns:
        Path to the generated SRT file or None if download failed
    """
    subtitle_url = entry_info.get('subtitle_url', '')
    title = entry_info.get('title', 'Unknown')
    episode_tag = entry_info.get('episode_tag', '')
    # episode_id = entry_info.get('episode_id', '')

    if not subtitle_url:
        message.subtitle_missing(title, episode_tag)
        return None

    # Create output directory if it doesn't exist
    ensure_dir_exists(PROCESSED_MEDIA_DIR)

    # Format file name in TV show style
    file_name = format_tv_style_filename(title, season_number, episode_tag)

    # Determine extension from URL
    extension = JSON_EXTENSION
    if '.ass' in subtitle_url.lower():
        extension = ASS_EXTENSION

    # Add language identifier
    lang_extension = f".en{extension}"

    # Download subtitle file
    subtitle_file_path = os.path.join(
        PROCESSED_MEDIA_DIR, f"{file_name}{lang_extension}")

    # Download the subtitle file
    if download_file(subtitle_url, subtitle_file_path):
        message.subtitle_download_success(title, episode_tag)

        # Convert JSON to SRT if it's a JSON file
        if extension == JSON_EXTENSION:
            # Create SRT file path with language identifier
            srt_file_path = subtitle_file_path.replace(
                lang_extension, f".en{SRT_EXTENSION}")
            if convert_json_to_srt(subtitle_file_path, srt_file_path):
                message.subtitle_convert_success(srt_file_path)
                return srt_file_path
        else:
            # For ASS files, just return the path
            message.info(f"Downloaded ASS subtitle: {subtitle_file_path}")
            return subtitle_file_path

    message.subtitle_process_failed(title, episode_tag)
    return None


def process_local_subtitle(season_folder, entry_json_path=None, season_number=1):
    """
    Process local subtitle files found in the vi folder.

    Args:
        season_folder: Path to the season folder
        entry_json_path: Path to the entry.json file (optional)
        season_number: Season number for TV style naming

    Returns:
        True if processing was successful, False otherwise
    """
    vi_folder = os.path.join(season_folder, SUBTITLE_FOLDER_NAME)
    if not os.path.exists(vi_folder):
        message.folder_not_found("subtitle", season_folder)
        return None

    # Get season info from entry.json
    title = os.path.basename(season_folder)  # Default to folder name
    episode_tag = ""

    if entry_json_path and os.path.exists(entry_json_path):
        entry_info = extract_info_from_entry_json(entry_json_path)
        title = entry_info.get('title', title)
        episode_tag = entry_info.get('episode_tag', '')

    # Format base filename in TV show style
    base_filename = format_tv_style_filename(title, season_number, episode_tag)

    # Create output directory if it doesn't exist
    ensure_dir_exists(PROCESSED_MEDIA_DIR)

    # Process JSON subtitle files
    subtitle_files = [f for f in os.listdir(
        vi_folder) if f.endswith(JSON_EXTENSION)]
    for subtitle_file in subtitle_files:
        json_path = os.path.join(vi_folder, subtitle_file)
        output_json_path = os.path.join(
            PROCESSED_MEDIA_DIR, f"{base_filename}.vi{JSON_EXTENSION}")

        # Copy the file if it doesn't exist at the destination
        if not os.path.exists(output_json_path):
            new_path = copy_file_with_new_name(
                json_path, PROCESSED_MEDIA_DIR, f"{base_filename}.vi{JSON_EXTENSION}")
            if new_path:
                message.info(f"Copied JSON subtitle: {new_path}")

        # Convert to SRT with language identifier
        srt_path = os.path.join(PROCESSED_MEDIA_DIR,
                                f"{base_filename}.vi{SRT_EXTENSION}")
        if convert_json_to_srt(output_json_path, srt_path):
            message.subtitle_convert_success(srt_path)

    # Handle ASS subtitle files - copy with language identifier
    ass_files = [f for f in os.listdir(vi_folder) if f.endswith(ASS_EXTENSION)]
    for ass_file in ass_files:
        ass_path = os.path.join(vi_folder, ass_file)
        output_ass_path = os.path.join(
            PROCESSED_MEDIA_DIR, f"{base_filename}.vi{ASS_EXTENSION}")

        # Copy to output directory
        if not os.path.exists(output_ass_path):
            new_path = copy_file_with_new_name(
                ass_path, PROCESSED_MEDIA_DIR, f"{base_filename}.vi{ASS_EXTENSION}")
            if new_path:
                message.info(f"Copied ASS subtitle: {new_path}")

    return True


def process_media_files(season_folder, season_number=1):
    """
    Process media files (audio.m4s and video.m4s) using the preferred video quality folder.
    Simply copies the files to the output directory with TV show naming convention.
    """
    # Get season info from entry.json
    entry_json_path = os.path.join(season_folder, ENTRY_JSON_FILENAME)
    entry_info = extract_info_from_entry_json(entry_json_path)

    title = entry_info.get('title', os.path.basename(season_folder))
    episode_tag = entry_info.get('episode_tag', '')

    # Get the preferred video quality folder name
    prefered_video_quality = entry_info.get('prefered_video_quality')
    if not prefered_video_quality:
        message.error(
            f"Could not determine video quality folder for {season_folder}")
        return None

    # Locate the media folder using the preferred quality
    media_folder = os.path.join(season_folder, prefered_video_quality)
    if not os.path.exists(media_folder):
        message.folder_not_found(
            f"video quality folder ({prefered_video_quality})", season_folder)
        return None

    # Create output folder for processed media
    ensure_dir_exists(PROCESSED_MEDIA_DIR)

    # Format filename in TV show style
    tv_style_filename = format_tv_style_filename(
        title, season_number, episode_tag)

    # Check if source files exist
    audio_path = os.path.join(media_folder, AUDIO_FILENAME)
    video_path = os.path.join(media_folder, VIDEO_FILENAME)

    if not (os.path.exists(audio_path) and os.path.exists(video_path)):
        message.media_files_missing(media_folder)
        return None

    # Copy the audio and video files to the output directory
    try:
        output_audio_filename = f"{tv_style_filename}{M4S_EXTENSION}"
        output_video_filename = f"{tv_style_filename}{MP4_EXTENSION}"

        output_audio_path = copy_file_with_new_name(
            audio_path, PROCESSED_MEDIA_DIR, output_audio_filename)
        output_video_path = copy_file_with_new_name(
            video_path, PROCESSED_MEDIA_DIR, output_video_filename)

        if output_audio_path and output_video_path:
            message.media_copied(title, PROCESSED_MEDIA_DIR)

        # Create a text file with metadata
        metadata_filename = f"{tv_style_filename}_metadata.txt"
        metadata_path = os.path.join(PROCESSED_MEDIA_DIR, metadata_filename)

        create_metadata_file(
            metadata_path,
            title,
            season_number,
            episode_tag,
            output_audio_path,
            output_video_path,
            season_folder
        )

        return {
            'audio': output_audio_path,
            'video': output_video_path,
            'metadata': metadata_path,
            'quality': prefered_video_quality
        }

    except Exception as e:
        message.error(f"Error copying media files for {title}: {str(e)}")
        return None


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

    # Process entry.json
    entry_json_path = os.path.join(season_folder, ENTRY_JSON_FILENAME)
    if os.path.exists(entry_json_path):
        entry_info = extract_info_from_entry_json(entry_json_path)
        download_en_subtitle(entry_info, season_number)
    else:
        message.file_not_found(ENTRY_JSON_FILENAME, season_folder)
        entry_json_path = None

    # Process subtitle files
    process_local_subtitle(season_folder, entry_json_path, season_number)

    # Process media files
    process_media_files(season_folder, season_number)

    return True


def process_all_seasons(bilibili_folder, season_number=1):
    """
    Process all anime seasons in the bilibili_video folder.
    This function recursively searches through folders to find season folders.
    A valid season folder is one that contains entry.json, or has 112 folder or vi folder.

    Args:
        bilibili_folder: Path to the bilibili_video folder
        season_number: Season number for TV style naming
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

    message.info(f"Found {len(season_folders)} anime episode folders")

    # Process each season folder
    for season_folder in season_folders:
        process_season_folder(season_folder, season_number)


def find_season_folders(parent_folder, max_depth=3, current_depth=0):
    """
    Recursively find anime season folders in the parent folder.

    Args:
        parent_folder: Parent folder to search
        max_depth: Maximum depth to search
        current_depth: Current depth in the search
    
    Returns:
        List of valid season folders
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
            # If not a valid season folder, search inside it (recursively)
            season_folders.extend(find_season_folders(
                folder, max_depth, current_depth + 1))

    return season_folders


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

    # Check for subtitle folder
    has_subtitle_folder = os.path.exists(
        os.path.join(folder_path, SUBTITLE_FOLDER_NAME))

    # Check for quality folders
    has_media_folder = False

    # If we have entry.json, try to extract preferred quality
    if has_entry_json:
        entry_info = extract_info_from_entry_json(
            os.path.join(folder_path, ENTRY_JSON_FILENAME))
        prefered_video_quality = entry_info.get('prefered_video_quality')

        # Check if the preferred quality folder exists
        if prefered_video_quality and os.path.exists(os.path.join(folder_path, prefered_video_quality)):
            has_media_folder = True

    # If no preferred quality found, check for any potential media folders
    if not has_media_folder:
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                # Check if this folder contains media files
                if (os.path.exists(os.path.join(item_path, AUDIO_FILENAME)) and
                        os.path.exists(os.path.join(item_path, VIDEO_FILENAME))):
                    has_media_folder = True
                    break

    return has_entry_json or has_media_folder or has_subtitle_folder


def get_season_number():
    """Get season number from user input."""
    while True:
        try:
            season_input = input("Enter the season number (1-99): ")
            season_number = int(season_input)
            if 1 <= season_number <= 99:
                return season_number
            else:
                message.info("Please enter a number between 1 and 99.")
        except ValueError:
            message.error("Please enter a valid number.")
