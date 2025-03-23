# `Bilibili` Anime Processing

A tool to process and organize anime content downloaded from the `Bilibili` Global version app. This utility helps manage media files, convert subtitles, and organize content into a consistent TV show format.

## Features

- Process anime seasons downloaded from `Bilibili` app
- Only support global version (Not China Version)
- Extract and process subtitle files (JSON and ASS formats)
- Convert JSON subtitles to SRT format
- Organize files with consistent TV show naming (e.g: {Anime Title} - S01E02)
- Identify and label subtitles by language (`.en` for English, `.vi` for local/original)
- Create metadata files with episode information
- Process nested folders to find all anime content

## Requirements

- Python 3.12 or higher
- `requests`, `ffmpeg-python` library
- FFMPEG has been assigned a BIN path in the system.
    - In Windows, it assign in Environment Variable
    - In Linux, MacOS just install it and it will available in SHELL

## Installation

1. Clone this repository or download the source code
2. Install the required dependencies:

    ```sh
    pip install requests ffmpeg-python
    ```

## Usage

- Run the application with:

    ```sh
    python app.py
    ```

- The script will prompt you to enter a season number for the anime. This helps organize your files in a TV show format (e.g., "{Anime Title} - S01E02").

### Folder Structure

- Create `bilibili_video` folder manually in main repository folder
- The application expects the following folder structure from `Bilibili` downloads:

```
bilibili_video/
├── [Anime Season]/
│   ├── [Episode 1]/
│   │   ├── 112/
│   │   │   ├── audio.m4s
│   │   │   └── video.m4s
│   │   ├── vi/
│   │   │   └── subtitle(.json or .ass)
│   │   └── entry.json
│   ├── [Episode 2]/
│   │   ├── 112/
│   │   │   ├── audio.m4s
│   │   │   └── video.m4s
│   │   ├── vi/
│   │   │   └── subtitle(.json or .ass)
│   │   └── entry.json
│   └── ...
```

- After processing, files will be organized in the `processed_media` directory with a consistent naming scheme:

```
processed_media/
├── Title - S01E01.m4s
├── Title - S01E01.mp4
├── Title - S01E01.vi(.srt or .ass)
├── Title - S01E01.en(.srt or .ass)
└── Title - S01E01_metadata.txt
```

## Project Structure

- `app.py` - Main application entry point
- `processing.py` - Core processing logic
- `jsonToSRT.py` - Utility to convert JSON subtitles to SRT format
- `utils.py` - Common utility functions
- `message.py` - Centralized message handling
- `config.py` - Configuration settings

## Notes

- ~~This tool does not handle video multiplexing. You will need to use an external tool to combine the final `.mkv` file~~
- This tool not support handle multiple `Anime Season` folder
- The season number is used for organizing files and does not affect the content itself.
- This is my personal tools so i only need Vietnamese and English version of subtitle.
- Feel free fork this repository and change the code if it necessary

## License

This repository is open source and available under the MIT License.
