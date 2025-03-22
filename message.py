"""Message handling for the application."""


def info(message):
    """Display an informational message."""
    print(f"[INFO] {message}")


def error(message):
    """Display an error message."""
    print(f"[ERROR] {message}")


def success(message):
    """Display a success message."""
    print(f"[SUCCESS] {message}")


def warning(message):
    """Display a warning message."""
    print(f"[WARNING] {message}")


def processing(item):
    """Display a processing message."""
    print(f"\n[PROCESSING] {item}")


# Subtitle related messages
def subtitle_missing(title, ep_page_tag):
    """Display a message for missing subtitle."""
    error(f"No English subtitle available for {title} - {ep_page_tag}")


def subtitle_download_success(title, ep_page_tag):
    """Display a message for successful subtitle download."""
    success(f"Downloaded subtitle for {title} - {ep_page_tag}")


def subtitle_convert_success(path):
    """Display a message for successful subtitle conversion."""
    success(f"Converted subtitle to SRT: {path}")


def subtitle_process_failed(title, ep_page_tag):
    """Display a message for failed subtitle processing."""
    error(
        f"Failed to download or convert subtitle for {title} - {ep_page_tag}")


# Folder and file related messages
def folder_not_found(folder_type, path):
    """Display a message for folder not found."""
    warning(f"No {folder_type} folder found in {path}")


def file_not_found(file_name, folder):
    """Display a message for file not found."""
    warning(f"No {file_name} found in {folder}")


# Media processing messages
def media_process_success(season_name):
    """Display a message for successful media processing."""
    success(f"Processed media files for {season_name}")


def media_files_missing(folder):
    """Display a message for missing media files."""
    warning(f"Missing media files in {folder}")


def media_copied(title, output_dir):
    """Display a message for copied media files."""
    success(f"Copied media files for {title} to {output_dir}")


# Season processing messages
def season_processing(season_name):
    """Display a message for processing a season."""
    processing(f"Season: {season_name}")


# JSON to SRT conversion messages
def json_to_srt_error(file_path, error_msg):
    """Display a message for JSON to SRT conversion error."""
    error(f"Error converting {file_path} to SRT: {error_msg}")


def json_to_srt_summary(count):
    """Display a summary of JSON to SRT conversion."""
    info(f"Processed {count} JSON files to SRT format.")
