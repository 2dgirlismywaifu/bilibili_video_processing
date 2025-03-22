import json
import os
from utils import format_srt_time, write_file
from config import DEFAULT_ENCODING, JSON_EXTENSION, SRT_EXTENSION
import message

def convert_json_to_srt(json_file_path, output_srt_path=None):
    """
    Convert a Bilibili subtitle JSON file to SRT format.
    
    Args:
        json_file_path: Path to the JSON subtitle file
        output_srt_path: Optional path for the output SRT file
        
    Returns:
        Path to the generated SRT file or None if conversion failed
    """
    try:
        with open(json_file_path, encoding=DEFAULT_ENCODING) as f:
            datas = json.load(f)

        srt_content = ''
        for i, data in enumerate(datas['body'], start=1):
            start = data['from']
            stop = data['to']
            content = data['content']
            
            # Add subtitle index
            srt_content += f"{i}\n"
            
            # Add time codes using the utility function
            srt_content += f"{format_srt_time(start)} --> {format_srt_time(stop)}\n"
            
            # Add subtitle content
            srt_content += f"{content}\n\n"

        # Determine output path
        if output_srt_path is None:
            output_srt_path = json_file_path.replace(JSON_EXTENSION, SRT_EXTENSION)
            
        # Write SRT file
        write_file(output_srt_path, srt_content)
        return output_srt_path
    
    except Exception as e:
        message.json_to_srt_error(json_file_path, str(e))
        return None

# This function can be called if this file is run as a script
def process_all_json_files_in_directory(directory='.'):
    """Process all JSON files in the given directory and convert them to SRT."""
    count = 0
    for filename in os.listdir(directory):
        if filename.endswith(JSON_EXTENSION):
            json_path = os.path.join(directory, filename)
            result = convert_json_to_srt(json_path)
            if result:
                count += 1
    
    return count

# Only run this if the file is executed directly
if __name__ == "__main__":
    processed = process_all_json_files_in_directory()
    message.json_to_srt_summary(processed)