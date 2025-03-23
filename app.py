from processing import clear_entry_info_cache, get_season_number, process_all_seasons
from config import BILIBILI_VIDEO_FOLDER
import message


season_number = get_season_number()
message.info(f"Processing anime as Season {season_number}")

# Process all seasons with the specified season number
process_all_seasons(BILIBILI_VIDEO_FOLDER, season_number)

# Clear cache when done
clear_entry_info_cache()