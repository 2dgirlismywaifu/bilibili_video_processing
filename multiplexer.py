"""
MKV Multiplexer for Bilibili anime processing.
Combines video, audio, and subtitles into a single MKV file.
Uses GPU acceleration when available.
"""

import os
import subprocess
import platform
import message
from config import SRT_EXTENSION, ASS_EXTENSION

# Global variable to store hardware acceleration information
# Will be populated during module initialization
HW_ACCEL = {
    'type': 'cpu',     # Default to CPU
    'hwaccel': None,   # Hardware acceleration option
    'encoder': 'copy'  # Default to stream copy (no re-encoding)
}


def detect_gpu():
    """
    Detect available GPUs for hardware acceleration.

    Returns:
        dict: Hardware acceleration details with type and options
    """
    global HW_ACCEL
    system = platform.system()
    
    # Helper function to check for specific GPU type
    def check_gpu(gpu_type, hwaccel, detection_configs):
        """Check if a specific GPU type is available"""
        for config in detection_configs:
            platform_type, command, search_terms = config
            
            if platform_type != 'all' and platform_type != system:
                continue
                
            try:
                result = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=5
                )
                
                # Check if any of the search terms are in the output
                if result.returncode == 0 and any(term in result.stdout for term in search_terms):
                    HW_ACCEL['type'] = gpu_type
                    HW_ACCEL['hwaccel'] = hwaccel
                    message.info(f"{gpu_type.upper()} GPU detected - using {hwaccel.upper()} hardware acceleration")
                    return True
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
                
        return False
    
    # GPU detection configurations: [(platform, command, search_terms), ...]
    gpu_configs = [
        # NVIDIA detection
        ('nvidia', 'cuda', [
            ('Windows', ['nvidia-smi', '-L'], ['GPU']),
            ('Linux', ['lspci'], ['NVIDIA'])
        ]),
        
        # AMD detection
        ('amd', 'amf', [
            ('Windows', ['wmic', 'path', 'win32_VideoController', 'get', 'name'], ['AMD', 'Radeon']),
            ('Linux', ['lspci'], ['AMD', 'Radeon'])
        ]),
        
        # Intel detection
        ('intel', 'qsv', [
            ('Windows', ['wmic', 'path', 'win32_VideoController', 'get', 'name'], ['Intel', 'UHD', 'HD Graphics']),
            ('Linux', ['lspci'], ['Intel'])
        ])
    ]
    
    # Try each GPU type in order of preference
    for gpu_type, hwaccel, configs in gpu_configs:
        if check_gpu(gpu_type, hwaccel, configs):
            return HW_ACCEL
    
    # If no GPU detected, default to CPU
    message.info("No GPU detected or suitable hardware acceleration found - using CPU")
    return HW_ACCEL


def multiplex_to_mkv(video_path, audio_path, output_mkv_path, subtitle_paths=None, title=None):
    """
    Multiplex video, audio, and subtitles into a single MKV file.
    Uses hardware acceleration when available.

    Args:
        video_path: Path to the video file
        audio_path: Path to the audio file
        output_mkv_path: Path for the output MKV file
        subtitle_paths: Dict of subtitle paths with language codes as keys
        title: The episode title (for messages and metadata)

    Returns:
        Path to the MKV file if successful, None otherwise
    """
    try:
        if not os.path.exists(video_path) or not os.path.exists(audio_path):
            message.error(
                f"Video or audio file not found: {video_path}, {audio_path}")
            return None

        # Use the globally detected hardware acceleration
        global HW_ACCEL

        # Prepare ffmpeg command
        command = ['ffmpeg', '-y']  # Overwrite output file if it exists

        # Add hardware acceleration
        if HW_ACCEL['hwaccel']:
            command.extend(['-hwaccel', HW_ACCEL['hwaccel']])

        # Add input files
        command.extend(['-i', video_path, '-i', audio_path])

        # Add subtitle inputs
        subtitle_idx = 2  # Start after video and audio
        if subtitle_paths and isinstance(subtitle_paths, dict):
            for lang_code, sub_path in subtitle_paths.items():
                if os.path.exists(sub_path):
                    command.extend(['-i', sub_path])
                    subtitle_idx += 1
                else:
                    message.warning(f"Subtitle file not found: {sub_path}")

        # Set codec options
        command.extend([
            '-c:v', 'copy',  # Copy video stream
            '-c:a', 'copy',  # Copy audio stream
            '-c:s', 'copy'   # Copy subtitle streams
        ])

        # Add subtitle metadata
        subtitle_idx = 0
        if subtitle_paths and isinstance(subtitle_paths, dict):
            for lang_code, sub_path in subtitle_paths.items():
                if os.path.exists(sub_path):
                    command.extend([
                        f'-metadata:s:s:{subtitle_idx}', f'language={lang_code}',
                        f'-metadata:s:s:{subtitle_idx}', f'title={lang_code.upper()} Subtitle'
                    ])
                    subtitle_idx += 1

        # Add output file
        command.append(output_mkv_path)

        # Log the command
        message.mkv_creation_started(
            title or os.path.basename(output_mkv_path))
        message.info(f"Using {HW_ACCEL['type'].upper()} for multiplexing")

        # Run ffmpeg command
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0 and os.path.exists(output_mkv_path):
            message.mkv_creation_success(output_mkv_path)
            return output_mkv_path
        else:
            message.error(f"FFmpeg error: {result.stderr}")

            # Try again with basic command if it failed
            if HW_ACCEL['type'] != 'cpu':
                message.warning(
                    "Hardware acceleration failed. Retrying with CPU...")
                # Basic command without hardware acceleration
                basic_command = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-i', audio_path,
                    '-c', 'copy',
                    output_mkv_path
                ]

                basic_result = subprocess.run(
                    basic_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if basic_result.returncode == 0 and os.path.exists(output_mkv_path):
                    message.mkv_creation_success(output_mkv_path)
                    return output_mkv_path
                else:
                    message.error(f"Basic FFmpeg error: {basic_result.stderr}")

            return None

    except Exception as e:
        message.mkv_creation_error(str(e))
        return None


# Detect GPU capabilities when the module is loaded
detect_gpu()
